from argparse import ArgumentParser
import multiprocessing as mp
import nevergrad as ng
import numpy as np

import mlir.iree_sandbox as sandbox
import mlir.ir as ir
import mlir.dialects.pdl as pdl
import mlir.dialects.linalg_transform as transform

from ..core.experts import *
from ..core.harness import *
from ..core.nevergrad_tuner_utils import *
from ..core.transforms import *
from ..core.utils import *

from ..contraction.definitions import EinsumProblem

################################################################################
### Problem instantiations.
################################################################################

keys = ['m', 'n', 'k']

# CHECK-NOT: FAILURE


# TODO: improve this to also generate good matcher constraints.
class NGScheduler:

  def __init__(self, problem_definition: ProblemDefinition,
               problem_sizes: Sequence[int]):
    # TODO: better factoring of these constants
    self.entry_point_name = 'main'
    self.fun_to_benchmark_name = 'matmul'

    self.problem_definition = problem_definition
    self.problem_sizes = problem_sizes

    # Init nevergrad's instrumentation.
    # TODO: better parametrization, for now this is enough to get a prototype.
    self.register_tile_sizes = ng.p.Choice(list(range(33)), repetitions=3)

    self.search_keyword = 'search_sizes'
    self.instrumentation = ng.p.Instrumentation(
        search_sizes=self.register_tile_sizes)
    self.optimizer = None

  def set_optimizer(self, search_strategy: str, budget: int):

    def constraints_fun(proposal):
      return dispatch_size_constraints_conjunction_satisfied( \
        self.problem_sizes, proposal, self.search_keyword)

    self.search_strategy = search_strategy
    self.optimizer = ng.optimizers.registry[self.search_strategy](
        parametrization=self.instrumentation, budget=budget)
    self.optimizer.parametrization.register_cheap_constraint(constraints_fun)

  # Unwrap the np.array from NG's ask() kwargs.
  def extract_search_sizes_from_proposal(self, proposal):
    return [x for x in proposal.kwargs[self.search_keyword]]

  # Optimizer may want to override our constraints set.
  def validate_proposal(self, proposal):
    if not size_constraints_conjunction_satisfied(
        self.problem_sizes, self.extract_search_sizes_from_proposal(proposal)):
      return False
    return True

  # TODO: generate a unique name for the matcher.
  # TODO: generate a tight matcher for the generic (e.g. isMatmulOp with
  # fixed size).
  def matcher(self, module, benefit: int = 1):
    pdl_pattern = None
    pdl_pattern_name = 'match_linalg_generic'
    with InsertionPoint(module.body):
      pdl_pattern = pdl.PatternOp(benefit=benefit, name=pdl_pattern_name)
      with ir.InsertionPoint(pdl_pattern.body):
        args = pdl.OperandsOp()
        types = pdl.TypesOp()
        # TODO: matcher constraints
        pdl_op = pdl.OperationOp('linalg.generic', args=[args], types=[types])
        pdl.RewriteOp(pdl_op, 'linalg_transform.apply')
    return pdl_pattern_name

  # TODO: more advanced schedules, atm we just TileAndVectorize.
  def schedule(self, module, proposal, benefit: int = 1):
    search_sizes = self.extract_search_sizes_from_proposal(proposal)

    print(f'Problem sizes: {self.problem_sizes}')
    print(f'Register tile sizes: {search_sizes}')

    # TODO: this is necessary to force-load the dialect, otherwise op creation
    # complains about "unregistered dialect" despite the registration called.
    register_sandbox_passes_and_dialects(module.context)
    module.context.dialects["linalg_transform"]

    nnz = np.count_nonzero(search_sizes)
    peel = [x for x in range(nnz)]
    peel = []  # TODO: enable peeling once handles are fixed.
    with InsertionPoint(module.body):
      pdl_pattern_name = self.matcher(module, benefit)
      sequence = transform.SequenceOp()
      with ir.InsertionPoint(sequence.body.blocks[0]):
        matched = transform.MatchOp(pdl_pattern_name)
        tiled = transform.TileOp(matched, sizes=search_sizes, peel=peel)
        transform.VectorizeOp(tiled, vectorize_padding=False)
        transform.BufferizeOp()
        for i in range(7):
          transform.LowerVectorsOp(stages=list(j + 1 for j in range(i + 1)))
        transform.LowerToLLVMOp()

  def save_module(self, module, module_save_filename):
    with open(module_save_filename, 'w') as f:
      f.write(str(module))
    print(f'Module saved in {module_save_filename}')

  def save_proposal_as_module(self,
                              proposal,
                              module_save_filename,
                              benefit: int = 1):
    with ir.Context() as ctx, ir.Location.unknown() as loc:
      module = Module.create()
      self.schedule(module, proposal, benefit)
      self.save_module(module, module_save_filename)


# Entry point to try compile and run while catching and reporting exceptions.
# This can run in interruptible multiprocess mode.
# ipc_dict must be provided, and it is used to return information across the
# root/children process boundary:
#   - 'throughputs': the measured throughputs.
#   - 'success': the return status.
def compile_and_run_checked_mp(problem: ProblemInstance, scheduler: NGScheduler,
                               proposal, n_iters: int, ipc_dict: dict):
  try:
    # Construct the schedule and save the module in case we need to replay later.
    def schedule_and_save(module):
      scheduler.schedule(module, proposal)
      # TODO: save and report on error.

    problem.compile_with_schedule_builder(
        entry_point_name=scheduler.entry_point_name,
        fun_to_benchmark_name=scheduler.fun_to_benchmark_name,
        compile_time_problem_sizes_dict={
            k: v for k, v in zip(keys, scheduler.problem_sizes)
        },
        schedule_builder=schedule_and_save)

    throughputs = problem.run(
        n_iters=n_iters,
        entry_point_name=scheduler.entry_point_name,
        runtime_problem_sizes_dict=problem.compile_time_problem_sizes_dict)

    ipc_dict['result'] = IPCState(success=True, throughputs=throughputs)
  except Exception as e:
    # TODO: save to replay errors.
    print(e)
    ipc_dict['result'] = IPCState(success=False, throughputs=None)


def bulk_synchronous_optim_loop(parsed_args):
  # Init random seed for reproducibility.
  np.random.seed(parsed_args.random_seed)

  assert len(
      parsed_args.problem_sizes_list) == 1, 'Single problem size supported atm'

  problem_definition = EinsumProblem('mk,kn', 'mnk', 2)
  # Create a schedule builder for fixed sizes.
  scheduler = NGScheduler(\
    problem_definition = problem_definition,
    problem_sizes = parsed_args.problem_sizes_list[0])

  manager = mp.Manager()
  for search_strategy in parsed_args.search_strategy:
    scheduler.set_optimizer(search_strategy, parsed_args.search_budget)

    # TODO: extract info from final recommendation instead of an auxiliary `throughputs` list
    throughputs = []
    for _ in range(0, parsed_args.search_budget,
                   parsed_args.num_compilation_processes):
      print(f'\n***********************************************')
      print(
          f'{search_strategy} optimization iter {_}/{parsed_args.search_budget}'
      )

      # 1. Launch `num_compilation_processes` compilation and "first-run" processes.
      ng_executions = []

      for _ in range(parsed_args.num_compilation_processes):
        proposal = scheduler.optimizer.ask()

        # Create problem instance, which holds the compiled module and the
        # ExecutionEngine.
        problem_instance = ProblemInstance(problem_definition, [np.float32] * 3)

        # The optimizer may chose to ignore our constraints.
        # Override this, do not evaluate and give it max cost.
        if not scheduler.validate_proposal(proposal):
          ng_executions.append(
              NGMPExecution(proposal=proposal,
                            problem_instances=None,
                            process=None,
                            ipc_state=None))
          continue

        # Start process that compiles and runs.
        ipc_dict = manager.dict()
        p = mp.Process(target=compile_and_run_checked_mp,
                       args=[
                           problem_instance, scheduler, proposal,
                           parsed_args.n_iters, ipc_dict
                       ])
        p.start()
        # Append NGMPExecution. After synchronization results will be available
        # in ipc_dict['result'].
        ng_executions.append(
            NGMPExecution(proposal=proposal,
                          problem_instance=problem_instance,
                          process=p,
                          ipc_dict=ipc_dict))

      # 2. Join all processes.
      join_bulk_synchronous_processes(ng_executions,
                                      parsed_args.timeout_per_compilation)

      # 3. Inspect the ipc_state.
      # This is the result of a noisy run but it is cheap to evaluate.
      for ng_mp_execution in ng_executions:
        ipc_state = ng_mp_execution.future_ipc_state()

        if not ipc_state.success:
          scheduler.optimizer.tell(ng_mp_execution.proposal, 1e9)
          continue

        process_throughputs = ipc_state.throughputs[
            parsed_args.metric_to_measure]
        # Calculate the relative distance to peak: invert the throughput @75%
        # (i.e. 5th computed quantile).
        # Lower is better.
        throughput = compute_quantiles(process_throughputs)[5]
        relative_error = \
          (parsed_args.machine_peak - throughput) / parsed_args.machine_peak
        scheduler.optimizer.tell(ng_mp_execution.proposal, relative_error)
        # TODO: extract info from final recommendation instead of an auxiliary `throughputs` list
        throughputs.append(throughput)

    # TODO: better handling of result saving, aggregation etc etc.
    final_module_filename = None
    if parsed_args.output_dir is not None:
      final_module_filename = f'{parsed_args.output_dir}/module.mlir'
    else:
      final_module_filename = '/tmp/module.mlir'

    recommendation = scheduler.optimizer.recommend()
    # TODO: extract info from final recommendation instead of an auxiliary `throughputs` list
    throughputs.sort()
    best = int(throughputs[-1])
    print(f'Best solution: {best} GUnits/s')
    scheduler.save_proposal_as_module(
        proposal=recommendation,
        module_save_filename=final_module_filename,
        benefit=best)


def main():
  print(f'Available optimizers\n{sorted(ng.optimizers.registry.keys())}')
  argparser = ArgumentParser()
  add_argparser_arguments(argparser, default_problem_sizes_list=[[16, 16, 16]])
  add_argparser_tuning_arguments(argparser)
  parsed_args = argparser.parse_args()
  bulk_synchronous_optim_loop(parsed_args=parsed_args)


if __name__ == '__main__':
  main()

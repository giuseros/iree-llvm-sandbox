// RUN: mlir-proto-opt -linalg-interp-transforms %s | FileCheck %s

// CHECK-LABEL: func @matmul_tensors(
// CHECK-SAME:    %[[TA:[0-9a-z]+]]: tensor<128x128xf32>
// CHECK-SAME:    %[[TB:[0-9a-z]+]]: tensor<128x128xf32>
// CHECK-SAME:    %[[TC:[0-9a-z]+]]: tensor<128x128xf32>
// CHECK-SAME:  -> tensor<128x128xf32> {
func @matmul_tensors(
  %arg0: tensor<128x128xf32>, %arg1: tensor<128x128xf32>, %arg2: tensor<128x128xf32> { linalg.inplaceable = true})
    -> tensor<128x128xf32> {
//      CHECK: %[[TD0:.*]] = scf.for {{.*}} to {{.*}} step {{.*}} iter_args(%[[TC0:.*]] = %[[TC]]) -> (tensor<128x128xf32>) {
//      CHECK:   %[[TD1:.*]] = scf.for {{.*}} to {{.*}} step {{.*}} iter_args(%[[TC1:.*]] = %[[TC0]]) -> (tensor<128x128xf32>) {
//      CHECK:     %[[TD2:.*]] = scf.for {{.*}} to {{.*}} step {{.*}} iter_args(%[[TC2:.*]] = %[[TC1]]) -> (tensor<128x128xf32>) {
//      CHECK:       %[[sTA:.*]] = tensor.extract_slice %[[TA]][{{.*}}] : tensor<128x128xf32> to tensor<4x4xf32>
//      CHECK:       %[[sTB:.*]] = tensor.extract_slice %[[TB]][{{.*}}] : tensor<128x128xf32> to tensor<4x4xf32>
//      CHECK:       %[[sTC:.*]] = tensor.extract_slice %[[TC2]][{{.*}}] : tensor<128x128xf32> to tensor<4x4xf32>
//      CHECK:       %[[sTD:.*]] = linalg.matmul {{.*}} ins(%[[sTA]], %[[sTB]] : tensor<4x4xf32>, tensor<4x4xf32>)
// CHECK-SAME:                                  outs(%[[sTC]] : tensor<4x4xf32>)  -> tensor<4x4xf32>
//      CHECK:       %[[TD:.*]] = tensor.insert_slice %[[sTD]] into %[[TC2]][{{.*}}]  : tensor<4x4xf32> into tensor<128x128xf32>
//      CHECK:       scf.yield %[[TD]] : tensor<128x128xf32>
//      CHECK:     scf.yield %[[TD2]] : tensor<128x128xf32>
//      CHECK:   scf.yield %[[TD1]] : tensor<128x128xf32>
  %0 = linalg.matmul  ins(%arg0, %arg1: tensor<128x128xf32>, tensor<128x128xf32>)
                     outs(%arg2: tensor<128x128xf32>)
    -> tensor<128x128xf32>

//      CHECK: return %[[TD0]] : tensor<128x128xf32>
  return %0 : tensor<128x128xf32>
}


pdl.pattern @pdl_target : benefit(1) {
  %args = operands
  %results = types
  %0 = operation "linalg.matmul"(%args : !pdl.range<value>) -> (%results : !pdl.range<type>)
  apply_native_constraint "nestedInFunc"[@matmul_tensors](%0 : !pdl.operation)
  // TODO: we don't want this, but it is the required terminator for pdl.pattern
  rewrite %0 with "linalg_transform.apply"
}

linalg_transform.sequence {
  %0 = match @pdl_target
  tile %0 {sizes = [4, 4, 4], pad = false}
}

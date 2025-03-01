// RUN: mlir-proto-opt %s -allow-unregistered-dialect -test-listener-canonicalize --split-input-file | FileCheck %s

//===----------------------------------------------------------------------===//
// Everything below copied from mlir/test/Dialect/Standard/canonicalize.mlir
//===----------------------------------------------------------------------===//

// CHECK-LABEL: @select_same_val
//       CHECK:   return %arg1
func @select_same_val(%arg0: i1, %arg1: i64) -> i64 {
  %0 = arith.select %arg0, %arg1, %arg1 : i64
  return %0 : i64
}

// -----

// CHECK-LABEL: @select_cmp_eq_select
//       CHECK:   return %arg1
func @select_cmp_eq_select(%arg0: i64, %arg1: i64) -> i64 {
  %0 = arith.cmpi eq, %arg0, %arg1 : i64
  %1 = arith.select %0, %arg0, %arg1 : i64
  return %1 : i64
}

// -----

// CHECK-LABEL: @select_cmp_ne_select
//       CHECK:   return %arg0
func @select_cmp_ne_select(%arg0: i64, %arg1: i64) -> i64 {
  %0 = arith.cmpi ne, %arg0, %arg1 : i64
  %1 = arith.select %0, %arg0, %arg1 : i64
  return %1 : i64
}

// -----

// CHECK-LABEL: @select_extui
//       CHECK:   %[[res:.+]] = arith.extui %arg0 : i1 to i64
//       CHECK:   return %[[res]]
func @select_extui(%arg0: i1) -> i64 {
  %c0_i64 = arith.constant 0 : i64
  %c1_i64 = arith.constant 1 : i64
  %res = arith.select %arg0, %c1_i64, %c0_i64 : i64
  return %res : i64
}

// CHECK-LABEL: @select_extui2
// CHECK-DAG:  %true = arith.constant true
// CHECK-DAG:  %[[xor:.+]] = arith.xori %arg0, %true : i1
// CHECK-DAG:  %[[res:.+]] = arith.extui %[[xor]] : i1 to i64
//       CHECK:   return %[[res]]
func @select_extui2(%arg0: i1) -> i64 {
  %c0_i64 = arith.constant 0 : i64
  %c1_i64 = arith.constant 1 : i64
  %res = arith.select %arg0, %c0_i64, %c1_i64 : i64
  return %res : i64
}

// -----

// CHECK-LABEL: @select_extui_i1
//  CHECK-NEXT:   return %arg0
func @select_extui_i1(%arg0: i1) -> i1 {
  %c0_i1 = arith.constant false
  %c1_i1 = arith.constant true
  %res = arith.select %arg0, %c1_i1, %c0_i1 : i1
  return %res : i1
}

// -----

// CHECK-LABEL: @branchCondProp
//       CHECK:       %[[trueval:.+]] = arith.constant true
//       CHECK:       %[[falseval:.+]] = arith.constant false
//       CHECK:       "test.consumer1"(%[[trueval]]) : (i1) -> ()
//       CHECK:       "test.consumer2"(%[[falseval]]) : (i1) -> ()
func @branchCondProp(%arg0: i1) {
  cf.cond_br %arg0, ^trueB, ^falseB

^trueB:
  "test.consumer1"(%arg0) : (i1) -> ()
  cf.br ^exit

^falseB:
  "test.consumer2"(%arg0) : (i1) -> ()
  cf.br ^exit

^exit:
  return
}

// -----

// CHECK-LABEL: @selToNot
//       CHECK:       %[[trueval:.+]] = arith.constant true
//       CHECK:       %{{.+}} = arith.xori %arg0, %[[trueval]] : i1
func @selToNot(%arg0: i1) -> i1 {
  %true = arith.constant true
  %false = arith.constant false
  %res = arith.select %arg0, %false, %true : i1
  return %res : i1
}


add_mlir_library(MLIRLinalgExtTransforms
  InParallelToAsync.cpp
  InParallelToSequentialFor.cpp
  TilingExternalModels.cpp
  TileToSequentialFor.cpp
  TileToInParallel.cpp
  Tiling.cpp
  TilingToTileOp.cpp
  Utils.cpp

  PARTIAL_SOURCES_INTENDED
  DEPENDS
  mlir-headers
  MLIRLinalgExt

  LINK_LIBS PUBLIC
  MLIRAffineToStandard
  MLIRAsync
  MLIRSCFToControlFlow
  MLIRLinalgToLLVM
  MLIRVectorToLLVM
  MLIRMathToLLVM
  MLIRMemRefToLLVM
  MLIRIR
  MLIRMath
  MLIRLinalg
  MLIRLinalgTransforms
  MLIRLinalgExt
  MLIRPass
  MLIRSCF
  MLIRTransforms
)

add_mlir_library(MLIRLinalgExtOpInterfaceImpl
  LinalgExtBufferization.cpp

  PARTIAL_SOURCES_INTENDED
  LINK_LIBS PUBLIC
  MLIRBufferization
  MLIRLinalgExt
  MLIRTensorTransforms
)

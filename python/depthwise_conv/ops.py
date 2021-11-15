# pytype: skip-file

from mlir.ir import *
from mlir.dialects.linalg.opdsl.lang import *


@linalg_structured_op
def depthwise_conv_1d_ncw_cw(
    I=TensorDef(TV.T1, S.N, S.C, S.OW * S.SW + S.KW * S.DW),
    K=TensorDef(TV.T2, S.C, S.KW),
    O=TensorDef(U, S.N, S.C, S.OW, output=True),
    strides=AttributeDef(S.SW),
    dilations=AttributeDef(S.DW)):
  implements(ConvolutionOpInterface)
  domain(D.n, D.c, D.ow, D.kw)
  O[D.n, D.c, D.ow] += (
      cast(U, I[D.n, D.c, D.ow * S.SW + D.kw * S.DW]) * cast(U, K[D.c, D.kw]))


@linalg_structured_op
def depthwise_conv_1d_ncw_wc(
    I=TensorDef(TV.T1, S.N, S.C, S.OW * S.SW + S.KW * S.DW),
    K=TensorDef(TV.T2, S.KW, S.C),
    O=TensorDef(U, S.N, S.C, S.OW, output=True),
    strides=AttributeDef(S.SW),
    dilations=AttributeDef(S.DW)):
  implements(ConvolutionOpInterface)
  domain(D.n, D.c, D.ow, D.kw)
  O[D.n, D.c, D.ow] += (
      cast(U, I[D.n, D.c, D.ow * S.SW + D.kw * S.DW]) * cast(U, K[D.kw, D.c]))


@linalg_structured_op
def depthwise_conv_1d_nwc_cw(
    I=TensorDef(TV.T1, S.N, S.OW * S.SW + S.KW * S.DW, S.C),
    K=TensorDef(TV.T2, S.C, S.KW),
    O=TensorDef(U, S.N, S.OW, S.C, output=True),
    strides=AttributeDef(S.SW),
    dilations=AttributeDef(S.DW)):
  implements(ConvolutionOpInterface)
  domain(D.n, D.ow, D.c, D.kw)
  O[D.n, D.ow, D.c] += (
      cast(U, I[D.n, D.ow * S.SW + D.kw * S.DW, D.c]) * cast(U, K[D.c, D.kw]))


@linalg_structured_op
def depthwise_conv_1d_nwc_wc(
    I=TensorDef(TV.T1, S.N, S.OW * S.SW + S.KW * S.DW, S.C),
    K=TensorDef(TV.T2, S.KW, S.C),
    O=TensorDef(U, S.N, S.OW, S.C, output=True),
    strides=AttributeDef(S.SW),
    dilations=AttributeDef(S.DW)):
  implements(ConvolutionOpInterface)
  domain(D.n, D.ow, D.c, D.kw)
  O[D.n, D.ow, D.c] += (
      cast(U, I[D.n, D.ow * S.SW + D.kw * S.DW, D.c]) * cast(U, K[D.kw, D.c]))


@linalg_structured_op
def depthwise_conv_1d_cnw_cw(
    I=TensorDef(TV.T1, S.C, S.N, S.OW * S.SW + S.KW * S.DW),
    K=TensorDef(TV.T2, S.C, S.KW),
    O=TensorDef(U, S.C, S.N, S.OW, output=True),
    strides=AttributeDef(S.SW),
    dilations=AttributeDef(S.DW)):
  implements(ConvolutionOpInterface)
  domain(D.c, D.n, D.ow, D.kw)
  O[D.c, D.n, D.ow] += (
      cast(U, I[D.c, D.n, D.ow * S.SW + D.kw * S.DW]) * cast(U, K[D.c, D.kw]))


@linalg_structured_op
def depthwise_conv_1d_cnw_wc(
    I=TensorDef(TV.T1, S.C, S.N, S.OW * S.SW + S.KW * S.DW),
    K=TensorDef(TV.T2, S.KW, S.C),
    O=TensorDef(U, S.C, S.N, S.OW, output=True),
    strides=AttributeDef(S.SW),
    dilations=AttributeDef(S.DW)):
  implements(ConvolutionOpInterface)
  domain(D.c, D.n, D.ow, D.kw)
  O[D.c, D.n, D.ow] += (
      cast(U, I[D.c, D.n, D.ow * S.SW + D.kw * S.DW]) * cast(U, K[D.kw, D.c]))


@linalg_structured_op
def depthwise_conv_1d_cwn_cw(
    I=TensorDef(TV.T1, S.C, S.OW * S.SW + S.KW * S.DW, S.N),
    K=TensorDef(TV.T2, S.C, S.KW),
    O=TensorDef(U, S.C, S.OW, S.N, output=True),
    strides=AttributeDef(S.SW),
    dilations=AttributeDef(S.DW)):
  implements(ConvolutionOpInterface)
  domain(D.c, D.ow, D.n, D.kw)
  O[D.c, D.ow, D.n] += (
      cast(U, I[D.c, D.ow * S.SW + D.kw * S.DW, D.n]) * cast(U, K[D.c, D.kw]))


@linalg_structured_op
def depthwise_conv_1d_cwn_wc(
    I=TensorDef(TV.T1, S.C, S.OW * S.SW + S.KW * S.DW, S.N),
    K=TensorDef(TV.T2, S.KW, S.C),
    O=TensorDef(U, S.C, S.OW, S.N, output=True),
    strides=AttributeDef(S.SW),
    dilations=AttributeDef(S.DW)):
  implements(ConvolutionOpInterface)
  domain(D.c, D.ow, D.n, D.kw)
  O[D.c, D.ow, D.n] += (
      cast(U, I[D.c, D.ow * S.SW + D.kw * S.DW, D.n]) * cast(U, K[D.kw, D.c]))


@linalg_structured_op
def depthwise_conv_1d_wnc_cw(
    I=TensorDef(TV.T1, S.OW * S.SW + S.KW * S.DW, S.N, S.C),
    K=TensorDef(TV.T2, S.C, S.KW),
    O=TensorDef(U, S.OW, S.N, S.C, output=True),
    strides=AttributeDef(S.SW),
    dilations=AttributeDef(S.DW)):
  implements(ConvolutionOpInterface)
  domain(D.ow, D.n, D.c, D.kw)
  O[D.ow, D.n, D.c] += (
      cast(U, I[D.ow * S.SW + D.kw * S.DW, D.n, D.c]) * cast(U, K[D.c, D.kw]))


@linalg_structured_op
def depthwise_conv_1d_wnc_wc(
    I=TensorDef(TV.T1, S.OW * S.SW + S.KW * S.DW, S.N, S.C),
    K=TensorDef(TV.T2, S.KW, S.C),
    O=TensorDef(U, S.OW, S.N, S.C, output=True),
    strides=AttributeDef(S.SW),
    dilations=AttributeDef(S.DW)):
  implements(ConvolutionOpInterface)
  domain(D.ow, D.n, D.c, D.kw)
  O[D.ow, D.n, D.c] += (
      cast(U, I[D.ow * S.SW + D.kw * S.DW, D.n, D.c]) * cast(U, K[D.kw, D.c]))


@linalg_structured_op
def depthwise_conv_1d_wcn_cw(
    I=TensorDef(TV.T1, S.OW * S.SW + S.KW * S.DW, S.C, S.N),
    K=TensorDef(TV.T2, S.C, S.KW),
    O=TensorDef(U, S.OW, S.C, S.N, output=True),
    strides=AttributeDef(S.SW),
    dilations=AttributeDef(S.DW)):
  implements(ConvolutionOpInterface)
  domain(D.ow, D.c, D.n, D.kw)
  O[D.ow, D.c, D.n] += (
      cast(U, I[D.ow * S.SW + D.kw * S.DW, D.c, D.n]) * cast(U, K[D.c, D.kw]))


@linalg_structured_op
def depthwise_conv_1d_wcn_wc(
    I=TensorDef(TV.T1, S.OW * S.SW + S.KW * S.DW, S.C, S.N),
    K=TensorDef(TV.T2, S.KW, S.C),
    O=TensorDef(U, S.OW, S.C, S.N, output=True),
    strides=AttributeDef(S.SW),
    dilations=AttributeDef(S.DW)):
  implements(ConvolutionOpInterface)
  domain(D.ow, D.c, D.n, D.kw)
  O[D.ow, D.c, D.n] += (
      cast(U, I[D.ow * S.SW + D.kw * S.DW, D.c, D.n]) * cast(U, K[D.kw, D.c]))
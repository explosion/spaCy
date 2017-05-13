from thinc.api import add, layerize, chain, clone, concatenate, with_flatten
from thinc.neural import Model, Maxout, Softmax, Affine
from thinc.neural._classes.hash_embed import HashEmbed
from thinc.neural.ops import NumpyOps, CupyOps

from thinc.neural._classes.convolution import ExtractWindow
from thinc.neural._classes.static_vectors import StaticVectors
from thinc.neural._classes.batchnorm import BatchNorm
from thinc.neural._classes.resnet import Residual
from thinc import describe
from thinc.describe import Dimension, Synapses, Biases, Gradient
from thinc.neural._classes.affine import _set_dimensions_if_needed
from .attrs import ID, LOWER, PREFIX, SUFFIX, SHAPE, TAG, DEP

import numpy


@describe.on_data(_set_dimensions_if_needed)
@describe.attributes(
    nI=Dimension("Input size"),
    nF=Dimension("Number of features"),
    nO=Dimension("Output size"),
    W=Synapses("Weights matrix",
        lambda obj: (obj.nO, obj.nF, obj.nI),
        lambda W, ops: ops.xavier_uniform_init(W)),
    b=Biases("Bias vector",
        lambda obj: (obj.nO,)),
    d_W=Gradient("W"),
    d_b=Gradient("b")
)
class PrecomputableAffine(Model):
    def __init__(self, nO=None, nI=None, nF=None, **kwargs):
        Model.__init__(self, **kwargs)
        self.nO = nO
        self.nI = nI
        self.nF = nF

    def begin_update(self, X, drop=0.):
        # X: (b, i)
        # Xf: (b, f, i)
        # dY: (b, o)
        # dYf: (b, f, o)
        #Yf = numpy.einsum('bi,ofi->bfo', X, self.W)
        Yf = self.ops.xp.tensordot(
                X, self.W, axes=[[1], [2]]).transpose((0, 2, 1))
        Yf += self.b
        def backward(dY_ids, sgd=None):
            dY, ids = dY_ids
            Xf = X[ids]

            #dW = numpy.einsum('bo,bfi->ofi', dY, Xf)
            dW = self.ops.xp.tensordot(dY, Xf, axes=[[0], [0]])
            db = dY.sum(axis=0)
            #dXf = numpy.einsum('bo,ofi->bfi', dY, self.W)
            dXf = self.ops.xp.tensordot(dY, self.W, axes=[[1], [0]])

            self.d_W += dW
            self.d_b += db

            if sgd is not None:
                sgd(self._mem.weights, self._mem.gradient, key=self.id)
            return dXf
        return Yf, backward


@describe.on_data(_set_dimensions_if_needed)
@describe.attributes(
    nI=Dimension("Input size"),
    nF=Dimension("Number of features"),
    nP=Dimension("Number of pieces"),
    nO=Dimension("Output size"),
    W=Synapses("Weights matrix",
        lambda obj: (obj.nF, obj.nO, obj.nP, obj.nI),
        lambda W, ops: ops.xavier_uniform_init(W)),
    b=Biases("Bias vector",
        lambda obj: (obj.nO, obj.nP)),
    d_W=Gradient("W"),
    d_b=Gradient("b")
)
class PrecomputableMaxouts(Model):
    def __init__(self, nO=None, nI=None, nF=None, pieces=3, **kwargs):
        Model.__init__(self, **kwargs)
        self.nO = nO
        self.nP = pieces
        self.nI = nI
        self.nF = nF

    def begin_update(self, X, drop=0.):
        # X: (b, i)
        # Yfp: (b, f, o, p)
        # Xf: (f, b, i)
        # dYp: (b, o, p)
        # W: (f, o, p, i)
        # b: (o, p)

        # bi,opfi->bfop
        # bop,fopi->bfi
        # bop,fbi->opfi : fopi

        tensordot = self.ops.xp.tensordot
        ascontiguous = self.ops.xp.ascontiguousarray

        Yfp = tensordot(X, self.W, axes=[[1], [3]])
        Yfp += self.b

        def backward(dYp_ids, sgd=None):
            dYp, ids = dYp_ids
            Xf = X[ids]

            dXf = tensordot(dYp, self.W, axes=[[1, 2], [1,2]])
            dW = tensordot(dYp, Xf, axes=[[0], [0]])

            self.d_W += dW.transpose((2, 0, 1, 3))
            self.d_b += dYp.sum(axis=0)

            if sgd is not None:
                sgd(self._mem.weights, self._mem.gradient, key=self.id)
            return dXf
        return Yfp, backward


def get_col(idx):
    def forward(X, drop=0.):
        if isinstance(X, numpy.ndarray):
            ops = NumpyOps()
        else:
            ops = CupyOps()
        assert len(X.shape) <= 3
        output = ops.xp.ascontiguousarray(X[:, idx])
        def backward(y, sgd=None):
            dX = ops.allocate(X.shape)
            dX[:, idx] += y
            return dX
        return output, backward
    return layerize(forward)


def zero_init(model):
    def _hook(self, X, y=None):
        self.W.fill(0)
    model.on_data_hooks.append(_hook)
    return model


def doc2feats(cols=None):
    cols = [ID, LOWER, PREFIX, SUFFIX, SHAPE]
    def forward(docs, drop=0.):
        feats = [doc.to_array(cols) for doc in docs]
        feats = [model.ops.asarray(f, dtype='uint64') for f in feats]
        return feats, None
    model = layerize(forward)
    model.cols = cols
    return model

def print_shape(prefix):
    def forward(X, drop=0.):
        return X, lambda dX, **kwargs: dX
    return layerize(forward)


@layerize
def get_token_vectors(tokens_attrs_vectors, drop=0.):
    ops = Model.ops
    tokens, attrs, vectors = tokens_attrs_vectors
    def backward(d_output, sgd=None):
        return (tokens, d_output)
    return vectors, backward


@layerize
def flatten(seqs, drop=0.):
    if isinstance(seqs[0], numpy.ndarray):
        ops = NumpyOps()
    else:
        ops = CupyOps()
    lengths = [len(seq) for seq in seqs]
    def finish_update(d_X, sgd=None):
        return ops.unflatten(d_X, lengths)
    X = ops.xp.vstack(seqs)
    return X, finish_update

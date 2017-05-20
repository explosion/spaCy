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
from .tokens.doc import Doc

import numpy


def _init_for_precomputed(W, ops):
    reshaped = W.reshape((W.shape[1], W.shape[0] * W.shape[2]))
    ops.xavier_uniform_init(reshaped)
    W[:] = reshaped.reshape(W.shape)

@describe.on_data(_set_dimensions_if_needed)
@describe.attributes(
    nI=Dimension("Input size"),
    nF=Dimension("Number of features"),
    nO=Dimension("Output size"),
    W=Synapses("Weights matrix",
        lambda obj: (obj.nF, obj.nO, obj.nI),
        lambda W, ops: _init_for_precomputed(W, ops)),
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
        # Yf: (b, f, i)
        # dY: (b, o)
        # dYf: (b, f, o)
        #Yf = numpy.einsum('bi,foi->bfo', X, self.W)
        Yf = self.ops.xp.tensordot(
                X, self.W, axes=[[1], [2]])
        Yf += self.b
        def backward(dY_ids, sgd=None):
            tensordot = self.ops.xp.tensordot
            dY, ids = dY_ids
            Xf = X[ids]

            #dXf = numpy.einsum('bo,foi->bfi', dY, self.W)
            dXf = tensordot(dY, self.W, axes=[[1], [1]])
            #dW = numpy.einsum('bo,bfi->ofi', dY, Xf)
            dW = tensordot(dY, Xf, axes=[[0], [0]])
            # ofi -> foi
            self.d_W += dW.transpose((1, 0, 2))
            self.d_b += dY.sum(axis=0)

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

def Tok2Vec(width, embed_size, preprocess=None):
    cols = [ID, LOWER, PREFIX, SUFFIX, SHAPE]
    with Model.define_operators({'>>': chain, '|': concatenate, '**': clone, '+': add}):
        lower = get_col(cols.index(LOWER))   >> HashEmbed(width, embed_size)
        prefix = get_col(cols.index(PREFIX)) >> HashEmbed(width, embed_size//2)
        suffix = get_col(cols.index(SUFFIX)) >> HashEmbed(width, embed_size//2)
        shape = get_col(cols.index(SHAPE))   >> HashEmbed(width, embed_size//2)

        tok2vec = (
            flatten
            >> (lower | prefix | suffix | shape )
            >> Maxout(width, width*4, pieces=3)
            >> Residual(ExtractWindow(nW=1) >> Maxout(width, width*3))
            >> Residual(ExtractWindow(nW=1) >> Maxout(width, width*3))
            >> Residual(ExtractWindow(nW=1) >> Maxout(width, width*3))
            >> Residual(ExtractWindow(nW=1) >> Maxout(width, width*3))
        )
        if preprocess not in (False, None):
            tok2vec = preprocess >> tok2vec
        # Work around thinc API limitations :(. TODO: Revise in Thinc 7
        tok2vec.nO = width
    return tok2vec


def foreach(layer):
    def forward(Xs, drop=0.):
        results = []
        backprops = []
        for X in Xs:
            result, bp = layer.begin_update(X, drop=drop)
            results.append(result)
            backprops.append(bp)
        def backward(d_results, sgd=None):
            dXs = []
            for d_result, backprop in zip(d_results, backprops):
                dXs.append(backprop(d_result, sgd))
            return dXs
        return results, backward
    model = layerize(forward)
    model._layers.append(layer)
    return model


def rebatch(size, layer):
    ops = layer.ops
    def forward(X, drop=0.):
        if X.shape[0] < size:
            return layer.begin_update(X)
        parts = _divide_array(X, size)
        results, bp_results = zip(*[layer.begin_update(p, drop=drop)
                                    for p in parts])
        y = ops.flatten(results)
        def backward(dy, sgd=None):
            d_parts = [bp(y, sgd=sgd) for bp, y in
                       zip(bp_results, _divide_array(dy, size))]
            try:
                dX = ops.flatten(d_parts)
            except TypeError:
                dX = None
            except ValueError:
                dX = None
            return dX
        return y, backward
    model = layerize(forward)
    model._layers.append(layer)
    return model


def _divide_array(X, size):
    parts = []
    index = 0
    while index < len(X):
        parts.append(X[index : index + size])
        index += size
    return parts


def get_col(idx):
    assert idx >= 0, idx
    def forward(X, drop=0.):
        assert idx >= 0, idx
        if isinstance(X, numpy.ndarray):
            ops = NumpyOps()
        else:
            ops = CupyOps()
        output = ops.xp.ascontiguousarray(X[:, idx], dtype=X.dtype)
        def backward(y, sgd=None):
            assert idx >= 0, idx
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
        feats = []
        for doc in docs:
            feats.append(
                model.ops.asarray(doc.to_array(cols),
                                  dtype='uint64'))
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
    elif hasattr(CupyOps.xp, 'ndarray') and isinstance(seqs[0], CupyOps.xp.ndarray):
        ops = CupyOps()
    else:
        raise ValueError("Unable to flatten sequence of type %s" % type(seqs[0]))
    lengths = [len(seq) for seq in seqs]
    def finish_update(d_X, sgd=None):
        return ops.unflatten(d_X, lengths)
    X = ops.xp.vstack(seqs)
    return X, finish_update

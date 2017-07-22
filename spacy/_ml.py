import ujson
from thinc.api import add, layerize, chain, clone, concatenate, with_flatten
from thinc.neural import Model, Maxout, Softmax, Affine
from thinc.neural._classes.hash_embed import HashEmbed
from thinc.neural.ops import NumpyOps, CupyOps
from thinc.neural.util import get_array_module

from thinc.neural._classes.convolution import ExtractWindow
from thinc.neural._classes.static_vectors import StaticVectors
from thinc.neural._classes.batchnorm import BatchNorm
from thinc.neural._classes.resnet import Residual
from thinc.neural import ReLu
from thinc import describe
from thinc.describe import Dimension, Synapses, Biases, Gradient
from thinc.neural._classes.affine import _set_dimensions_if_needed
from thinc.api import FeatureExtracter, with_getitem
from thinc.neural.pooling import Pooling, max_pool, mean_pool

from .attrs import ID, ORTH, LOWER, NORM, PREFIX, SUFFIX, SHAPE, TAG, DEP
from .tokens.doc import Doc

import numpy
import io


@layerize
def _flatten_add_lengths(seqs, pad=0, drop=0.):
    ops = Model.ops
    lengths = ops.asarray([len(seq) for seq in seqs], dtype='i')
    def finish_update(d_X, sgd=None):
        return ops.unflatten(d_X, lengths, pad=pad)
    X = ops.flatten(seqs, pad=pad)
    return (X, lengths), finish_update


@layerize
def _logistic(X, drop=0.):
    xp = get_array_module(X)
    if not isinstance(X, xp.ndarray):
        X = xp.asarray(X)
    # Clip to range (-10, 10)
    X = xp.minimum(X, 10., X)
    X = xp.maximum(X, -10., X)
    Y = 1. / (1. + xp.exp(-X))
    def logistic_bwd(dY, sgd=None):
        dX = dY * (Y * (1-Y))
        return dX
    return Y, logistic_bwd


def _zero_init(model):
    def _zero_init_impl(self, X, y):
        self.W.fill(0)
    model.on_data_hooks.append(_zero_init_impl)
    if model.W is not None:
        model.W.fill(0.)
    return model

@layerize
def _preprocess_doc(docs, drop=0.):
    keys = [doc.to_array([LOWER]) for doc in docs]
    keys = [a[:, 0] for a in keys]
    ops = Model.ops
    lengths = ops.asarray([arr.shape[0] for arr in keys])
    keys = ops.xp.concatenate(keys)
    vals = ops.allocate(keys.shape[0]) + 1
    return (keys, vals, lengths), None



def _init_for_precomputed(W, ops):
    if (W**2).sum() != 0.:
        return
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
    def __init__(self, nO=None, nI=None, nF=None, nP=3, **kwargs):
        Model.__init__(self, **kwargs)
        self.nO = nO
        self.nP = nP
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
    cols = [ID, NORM, PREFIX, SUFFIX, SHAPE]
    with Model.define_operators({'>>': chain, '|': concatenate, '**': clone, '+': add}):
        norm = get_col(cols.index(NORM))   >> HashEmbed(width, embed_size, name='embed_lower')
        prefix = get_col(cols.index(PREFIX)) >> HashEmbed(width, embed_size//2, name='embed_prefix')
        suffix = get_col(cols.index(SUFFIX)) >> HashEmbed(width, embed_size//2, name='embed_suffix')
        shape = get_col(cols.index(SHAPE))   >> HashEmbed(width, embed_size//2, name='embed_shape')

        embed = (norm | prefix | suffix | shape )
        tok2vec = (
            with_flatten(
                asarray(Model.ops, dtype='uint64')
                >> embed
                >> Maxout(width, width*4, pieces=3)
                >> Residual(ExtractWindow(nW=1) >> Maxout(width, width*3))
                >> Residual(ExtractWindow(nW=1) >> Maxout(width, width*3))
                >> Residual(ExtractWindow(nW=1) >> Maxout(width, width*3))
                >> Residual(ExtractWindow(nW=1) >> Maxout(width, width*3)),
            pad=4)
        )
        if preprocess not in (False, None):
            tok2vec = preprocess >> tok2vec
        # Work around thinc API limitations :(. TODO: Revise in Thinc 7
        tok2vec.nO = width
        tok2vec.embed = embed
    return tok2vec


def asarray(ops, dtype):
    def forward(X, drop=0.):
        return ops.asarray(X, dtype=dtype), None
    return layerize(forward)


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
    cols = [ID, NORM, PREFIX, SUFFIX, SHAPE]
    def forward(docs, drop=0.):
        feats = []
        for doc in docs:
            feats.append(doc.to_array(cols))
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


@layerize
def logistic(X, drop=0.):
    xp = get_array_module(X)
    if not isinstance(X, xp.ndarray):
        X = xp.asarray(X)
    # Clip to range (-10, 10)
    X = xp.minimum(X, 10., X)
    X = xp.maximum(X, -10., X)
    Y = 1. / (1. + xp.exp(-X))
    def logistic_bwd(dY, sgd=None):
        dX = dY * (Y * (1-Y))
        return dX
    return Y, logistic_bwd


def zero_init(model):
    def _zero_init_impl(self, X, y):
        self.W.fill(0)
    model.on_data_hooks.append(_zero_init_impl)
    return model

@layerize
def preprocess_doc(docs, drop=0.):
    keys = [doc.to_array([LOWER]) for doc in docs]
    keys = [a[:, 0] for a in keys]
    ops = Model.ops
    lengths = ops.asarray([arr.shape[0] for arr in keys])
    keys = ops.xp.concatenate(keys)
    vals = ops.allocate(keys.shape[0]) + 1
    return (keys, vals, lengths), None


# This belongs in thinc
def wrap(func, *child_layers):
    model = layerize(func)
    model._layers.extend(child_layers)
    def on_data(self, X, y):
        for child in self._layers:
            for hook in child.on_data_hooks:
                hook(child, X, y)
    model.on_data_hooks.append(on_data)
    return model

# This belongs in thinc
def uniqued(layer, column=0):
    '''Group inputs to a layer, so that the layer only has to compute
    for the unique values. The data is transformed back before output, and the same
    transformation is applied for the gradient. Effectively, this is a cache
    local to each minibatch.

    The uniqued wrapper is useful for word inputs, because common words are
    seen often, but we may want to compute complicated features for the words,
    using e.g. character LSTM.
    '''
    def uniqued_fwd(X, drop=0.):
        keys = X[:, column]
        if not isinstance(keys, numpy.ndarray):
            keys = keys.get()
        uniq_keys, ind, inv, counts = numpy.unique(keys, return_index=True,
                                                    return_inverse=True,
                                                    return_counts=True)
        Y_uniq, bp_Y_uniq = layer.begin_update(X[ind], drop=drop)
        Y = Y_uniq[inv].reshape((X.shape[0],) + Y_uniq.shape[1:])
        def uniqued_bwd(dY, sgd=None):
            dY_uniq = layer.ops.allocate(Y_uniq.shape, dtype='f')
            layer.ops.scatter_add(dY_uniq, inv, dY)
            d_uniques = bp_Y_uniq(dY_uniq, sgd=sgd)
            if d_uniques is not None:
                dX = (d_uniques / counts)[inv]
                return dX
            else:
                return None
        return Y, uniqued_bwd
    model = wrap(uniqued_fwd, layer)
    return model


def build_text_classifier(nr_class, width=64, **cfg):
    nr_vector = cfg.get('nr_vector', 1000)
    with Model.define_operators({'>>': chain, '+': add, '|': concatenate, '**': clone}):
        embed_lower = HashEmbed(width, nr_vector, column=1)
        embed_prefix = HashEmbed(width//2, nr_vector, column=2)
        embed_suffix = HashEmbed(width//2, nr_vector, column=3)
        embed_shape = HashEmbed(width//2, nr_vector, column=4)

        model = (
            FeatureExtracter([ORTH, LOWER, PREFIX, SUFFIX, SHAPE])
            >> _flatten_add_lengths
            >> with_getitem(0,
                uniqued(
                    (embed_lower | embed_prefix | embed_suffix | embed_shape) 
                    >> Maxout(width, width+(width//2)*3)
                )
                >> Residual(ExtractWindow(nW=1) >> ReLu(width, width*3))
                >> Residual(ExtractWindow(nW=1) >> ReLu(width, width*3))
                >> Residual(ExtractWindow(nW=1) >> ReLu(width, width*3))
            )
            >> Pooling(mean_pool, max_pool)
            >> Residual(ReLu(width*2, width*2))
            >> zero_init(Affine(nr_class, width*2, drop_factor=0.0))
            >> logistic
        )
    model.lsuv = False
    return model


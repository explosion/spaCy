import ujson
from thinc.api import add, layerize, chain, clone, concatenate, with_flatten
from thinc.neural import Model, Maxout, Softmax, Affine
from thinc.neural._classes.hash_embed import HashEmbed
from thinc.neural.ops import NumpyOps, CupyOps
from thinc.neural.util import get_array_module
import random
import cytoolz

from thinc.neural._classes.convolution import ExtractWindow
from thinc.neural._classes.static_vectors import StaticVectors
from thinc.neural._classes.batchnorm import BatchNorm as BN
from thinc.neural._classes.layernorm import LayerNorm as LN
from thinc.neural._classes.resnet import Residual
from thinc.neural import ReLu
from thinc.neural._classes.selu import SELU
from thinc import describe
from thinc.describe import Dimension, Synapses, Biases, Gradient
from thinc.neural._classes.affine import _set_dimensions_if_needed
from thinc.api import FeatureExtracter, with_getitem
from thinc.neural.pooling import Pooling, max_pool, mean_pool, sum_pool
from thinc.neural._classes.attention import ParametricAttention
from thinc.linear.linear import LinearModel
from thinc.api import uniqued, wrap, flatten_add_lengths, noop


from .attrs import ID, ORTH, LOWER, NORM, PREFIX, SUFFIX, SHAPE, TAG, DEP, CLUSTER
from .tokens.doc import Doc
from . import util

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


@layerize
def add_tuples(X, drop=0.):
    """Give inputs of sequence pairs, where each sequence is (vals, length),
    sum the values, returning a single sequence.

    If input is:
    ((vals1, length), (vals2, length)
    Output is:
    (vals1+vals2, length)

    vals are a single tensor for the whole batch.
    """
    (vals1, length1), (vals2, length2) = X
    assert length1 == length2

    def add_tuples_bwd(dY, sgd=None):
        return (dY, dY)

    return (vals1+vals2, length), add_tuples_bwd


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


def drop_layer(layer, factor=2.):
    def drop_layer_fwd(X, drop=0.):
        if drop <= 0.:
            return layer.begin_update(X, drop=drop)
        else:
            coinflip = layer.ops.xp.random.random()
            if (coinflip / factor) >= drop:
                return layer.begin_update(X, drop=drop)
            else:
                return X, lambda dX, sgd=None: dX

    model = wrap(drop_layer_fwd, layer)
    model.predict = layer
    return model


def Tok2Vec(width, embed_size, pretrained_dims=0):
    if pretrained_dims is None:
        pretrained_dims = 0
    cols = [ID, NORM, PREFIX, SUFFIX, SHAPE, ORTH]
    with Model.define_operators({'>>': chain, '|': concatenate, '**': clone, '+': add}):
        norm = HashEmbed(width, embed_size, column=cols.index(NORM), name='embed_norm')
        prefix = HashEmbed(width, embed_size//2, column=cols.index(PREFIX), name='embed_prefix')
        suffix = HashEmbed(width, embed_size//2, column=cols.index(SUFFIX), name='embed_suffix')
        shape = HashEmbed(width, embed_size//2, column=cols.index(SHAPE), name='embed_shape')

        trained_vectors = (
            FeatureExtracter(cols)
            >> with_flatten(
                uniqued(
                    (norm | prefix | suffix | shape)
                    >> LN(Maxout(width, width*4, pieces=3)), column=5)
            )
        )
        convolution = Residual(ExtractWindow(nW=1) >> LN(Maxout(width, width*3, pieces=3)))

        if pretrained_dims >= 1:
            embed = concatenate_lists(trained_vectors, SpacyVectors)
            tok2vec = (
                embed
                >> with_flatten(
                    Affine(width, width+pretrained_dims)
                    >> convolution ** 4,
                    pad=4)
            )
        else:
            embed = trained_vectors
            tok2vec = (
                embed
                >> with_flatten(convolution ** 4, pad=4)
            )

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
    if cols is None:
        cols = [ID, NORM, PREFIX, SUFFIX, SHAPE, ORTH]
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


def fine_tune(embedding, combine=None):
    if combine is not None:
        raise NotImplementedError(
            "fine_tune currently only supports addition. Set combine=None")
    def fine_tune_fwd(docs_tokvecs, drop=0.):
        docs, tokvecs = docs_tokvecs

        lengths = model.ops.asarray([len(doc) for doc in docs], dtype='i')

        vecs, bp_vecs = embedding.begin_update(docs, drop=drop)
        flat_tokvecs = embedding.ops.flatten(tokvecs)
        flat_vecs = embedding.ops.flatten(vecs)
        output = embedding.ops.unflatten(
                   (model.mix[0] * flat_tokvecs + model.mix[1] * flat_vecs), lengths)

        def fine_tune_bwd(d_output, sgd=None):
            flat_grad = model.ops.flatten(d_output)
            model.d_mix[0] += flat_tokvecs.dot(flat_grad.T).sum()
            model.d_mix[1] += flat_vecs.dot(flat_grad.T).sum()

            bp_vecs([d_o * model.mix[1] for d_o in d_output], sgd=sgd)
            if sgd is not None:
                sgd(model._mem.weights, model._mem.gradient, key=model.id)
            return [d_o * model.mix[0] for d_o in d_output]
        return output, fine_tune_bwd

    def fine_tune_predict(docs_tokvecs):
        docs, tokvecs = docs_tokvecs
        vecs = embedding(docs)
        return [model.mix[0]*tv+model.mix[1]*v
                for tv, v in zip(tokvecs, vecs)]

    model = wrap(fine_tune_fwd, embedding)
    model.mix = model._mem.add((model.id, 'mix'), (2,))
    model.mix.fill(0.5)
    model.d_mix = model._mem.add_gradient((model.id, 'd_mix'), (model.id, 'mix'))
    model.predict = fine_tune_predict
    return model


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

def getitem(i):
    def getitem_fwd(X, drop=0.):
        return X[i], None
    return layerize(getitem_fwd)

def build_tagger_model(nr_class, token_vector_width, pretrained_dims=0, **cfg):
    embed_size = util.env_opt('embed_size', 4000)
    with Model.define_operators({'>>': chain, '+': add}):
        # Input: (doc, tensor) tuples
        private_tok2vec = Tok2Vec(token_vector_width, embed_size,
                                  pretrained_dims=pretrained_dims)
        model = (
            fine_tune(private_tok2vec)
            >> with_flatten(
                Maxout(token_vector_width, token_vector_width)
                >> Softmax(nr_class, token_vector_width)
            )
        )
    model.nI = None
    return model


@layerize
def SpacyVectors(docs, drop=0.):
    xp = get_array_module(docs[0].vocab.vectors.data)
    width = docs[0].vocab.vectors.data.shape[1]
    batch = []
    for doc in docs:
        indices = numpy.zeros((len(doc),), dtype='i')
        for i, word in enumerate(doc):
            if word.orth in doc.vocab.vectors.key2row:
                indices[i] = doc.vocab.vectors.key2row[word.orth]
            else:
                indices[i] = 0
        vectors = doc.vocab.vectors.data[indices]
        batch.append(vectors)
    return batch, None


def foreach(layer, drop_factor=1.0):
    '''Map a layer across elements in a list'''
    def foreach_fwd(Xs, drop=0.):
        drop *= drop_factor
        ys = []
        backprops = []
        for X in Xs:
            y, bp_y = layer.begin_update(X, drop=drop)
            ys.append(y)
            backprops.append(bp_y)
        def foreach_bwd(d_ys, sgd=None):
            d_Xs = []
            for d_y, bp_y in zip(d_ys, backprops):
                if bp_y is not None and bp_y is not None:
                    d_Xs.append(d_y, sgd=sgd)
                else:
                    d_Xs.append(None)
            return d_Xs
        return ys, foreach_bwd
    model = wrap(foreach_fwd, layer)
    return model


def build_text_classifier(nr_class, width=64, **cfg):
    nr_vector = cfg.get('nr_vector', 5000)
    with Model.define_operators({'>>': chain, '+': add, '|': concatenate,
                                 '**': clone}):
        if cfg.get('low_data'):
            model = (
                SpacyVectors
                >> flatten_add_lengths
                >> with_getitem(0,
                    Affine(width, 300)
                )
                >> ParametricAttention(width)
                >> Pooling(sum_pool)
                >> Residual(ReLu(width, width)) ** 2
                >> zero_init(Affine(nr_class, width, drop_factor=0.0))
                >> logistic
            )
            return model


        lower = HashEmbed(width, nr_vector, column=1)
        prefix = HashEmbed(width//2, nr_vector, column=2)
        suffix = HashEmbed(width//2, nr_vector, column=3)
        shape = HashEmbed(width//2, nr_vector, column=4)

        trained_vectors = (
            FeatureExtracter([ORTH, LOWER, PREFIX, SUFFIX, SHAPE, ID])
            >> with_flatten(
                uniqued(
                    (lower | prefix | suffix | shape)
                    >> LN(Maxout(width, width+(width//2)*3)),
                    column=0
                )
            )
        )

        static_vectors = (
            SpacyVectors
            >> with_flatten(Affine(width, 300))
        )

        cnn_model = (
            # TODO Make concatenate support lists
            concatenate_lists(trained_vectors, static_vectors)
            >> with_flatten(
                LN(Maxout(width, width*2))
                >> Residual(
                    (ExtractWindow(nW=1) >> zero_init(Maxout(width, width*3)))
                ) ** 2, pad=2
            )
            >> flatten_add_lengths
            >> ParametricAttention(width)
            >> Pooling(sum_pool)
            >> Residual(zero_init(Maxout(width, width)))
            >> zero_init(Affine(nr_class, width, drop_factor=0.0))
        )

        linear_model = (
            _preprocess_doc
            >> LinearModel(nr_class, drop_factor=0.)
        )

        model = (
            (linear_model | cnn_model)
            >> zero_init(Affine(nr_class, nr_class*2, drop_factor=0.0))
            >> logistic
        )

    model.lsuv = False
    return model

@layerize
def flatten(seqs, drop=0.):
    ops = Model.ops
    lengths = ops.asarray([len(seq) for seq in seqs], dtype='i')
    def finish_update(d_X, sgd=None):
        return ops.unflatten(d_X, lengths, pad=0)
    X = ops.flatten(seqs, pad=0)
    return X, finish_update


def concatenate_lists(*layers, **kwargs): # pragma: no cover
    '''Compose two or more models `f`, `g`, etc, such that their outputs are
    concatenated, i.e. `concatenate(f, g)(x)` computes `hstack(f(x), g(x))`
    '''
    if not layers:
        return noop()
    drop_factor = kwargs.get('drop_factor', 1.0)
    ops = layers[0].ops
    layers = [chain(layer, flatten) for layer in layers]
    concat = concatenate(*layers)
    def concatenate_lists_fwd(Xs, drop=0.):
        drop *= drop_factor
        lengths = ops.asarray([len(X) for X in Xs], dtype='i')
        flat_y, bp_flat_y = concat.begin_update(Xs, drop=drop)
        ys = ops.unflatten(flat_y, lengths)
        def concatenate_lists_bwd(d_ys, sgd=None):
            return bp_flat_y(ops.flatten(d_ys), sgd=sgd)
        return ys, concatenate_lists_bwd
    model = wrap(concatenate_lists_fwd, concat)
    return model



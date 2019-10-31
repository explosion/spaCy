# coding: utf8
from __future__ import unicode_literals
from thinc.v2v import Model, Maxout
from thinc.i2v import HashEmbed, StaticVectors
from thinc.t2t import ExtractWindow
from thinc.misc import Residual
from thinc.misc import LayerNorm as LN
from thinc.misc import FeatureExtracter
from thinc.api import layerize, chain, clone, concatenate, with_flatten
from thinc.api import uniqued, wrap, noop
from thinc.api import with_square_sequences
from thinc.neural.util import copy_array

from thinc import describe
from thinc.describe import Dimension, Synapses, Gradient

from ..attrs import ID, ORTH, NORM, PREFIX, SUFFIX, SHAPE


def Tok2Vec(width, embed_size, **kwargs):
    pretrained_vectors = kwargs.get("pretrained_vectors", None)
    cnn_maxout_pieces = kwargs.get("cnn_maxout_pieces", 3)
    subword_features = kwargs.get("subword_features", True)
    char_embed = kwargs.get("char_embed", False)
    if char_embed:
        subword_features = False
    conv_depth = kwargs.get("conv_depth", 4)
    bilstm_depth = kwargs.get("bilstm_depth", 0)
    cols = [ID, NORM, PREFIX, SUFFIX, SHAPE, ORTH]
    with Model.define_operators({">>": chain, "|": concatenate, "**": clone}):
        norm = HashEmbed(width, embed_size, column=cols.index(NORM), name="embed_norm")
        if subword_features:
            prefix = HashEmbed(
                width, embed_size // 2, column=cols.index(PREFIX), name="embed_prefix"
            )
            suffix = HashEmbed(
                width, embed_size // 2, column=cols.index(SUFFIX), name="embed_suffix"
            )
            shape = HashEmbed(
                width, embed_size // 2, column=cols.index(SHAPE), name="embed_shape"
            )
        else:
            prefix, suffix, shape = (None, None, None)
        if pretrained_vectors is not None:
            glove = StaticVectors(pretrained_vectors, width, column=cols.index(ID))

            if subword_features:
                embed = uniqued(
                    (glove | norm | prefix | suffix | shape)
                    >> LN(Maxout(width, width * 5, pieces=3)),
                    column=cols.index(ORTH),
                )
            else:
                embed = uniqued(
                    (glove | norm) >> LN(Maxout(width, width * 2, pieces=3)),
                    column=cols.index(ORTH),
                )
        elif subword_features:
            embed = uniqued(
                (norm | prefix | suffix | shape)
                >> LN(Maxout(width, width * 4, pieces=3)),
                column=cols.index(ORTH),
            )
        elif char_embed:
            embed = concatenate_lists(
                CharacterEmbed(nM=64, nC=8),
                FeatureExtracter(cols) >> with_flatten(norm),
            )
            reduce_dimensions = LN(
                Maxout(width, 64 * 8 + width, pieces=cnn_maxout_pieces)
            )
        else:
            embed = norm

        convolution = Residual(
            ExtractWindow(nW=1)
            >> LN(Maxout(width, width * 3, pieces=cnn_maxout_pieces))
        )
        if char_embed:
            tok2vec = embed >> with_flatten(
                reduce_dimensions >> convolution ** conv_depth, pad=conv_depth
            )
        else:
            tok2vec = FeatureExtracter(cols) >> with_flatten(
                embed >> convolution ** conv_depth, pad=conv_depth
            )

        if bilstm_depth >= 1:
            tok2vec = tok2vec >> PyTorchBiLSTM(width, width, bilstm_depth)
        # Work around thinc API limitations :(. TODO: Revise in Thinc 7
        tok2vec.nO = width
        tok2vec.embed = embed
    return tok2vec


@layerize
def flatten(seqs, drop=0.0):
    ops = Model.ops
    lengths = ops.asarray([len(seq) for seq in seqs], dtype="i")

    def finish_update(d_X, sgd=None):
        return ops.unflatten(d_X, lengths, pad=0)

    X = ops.flatten(seqs, pad=0)
    return X, finish_update


def concatenate_lists(*layers, **kwargs):  # pragma: no cover
    """Compose two or more models `f`, `g`, etc, such that their outputs are
    concatenated, i.e. `concatenate(f, g)(x)` computes `hstack(f(x), g(x))`
    """
    if not layers:
        return noop()
    drop_factor = kwargs.get("drop_factor", 1.0)
    ops = layers[0].ops
    layers = [chain(layer, flatten) for layer in layers]
    concat = concatenate(*layers)

    def concatenate_lists_fwd(Xs, drop=0.0):
        if drop is not None:
            drop *= drop_factor
        lengths = ops.asarray([len(X) for X in Xs], dtype="i")
        flat_y, bp_flat_y = concat.begin_update(Xs, drop=drop)
        ys = ops.unflatten(flat_y, lengths)

        def concatenate_lists_bwd(d_ys, sgd=None):
            return bp_flat_y(ops.flatten(d_ys), sgd=sgd)

        return ys, concatenate_lists_bwd

    model = wrap(concatenate_lists_fwd, concat)
    return model


def _uniform_init(lo, hi):
    def wrapped(W, ops):
        copy_array(W, ops.xp.random.uniform(lo, hi, W.shape))

    return wrapped


@describe.attributes(
    nM=Dimension("Vector dimensions"),
    nC=Dimension("Number of characters per word"),
    vectors=Synapses(
        "Embed matrix", lambda obj: (obj.nC, obj.nV, obj.nM), _uniform_init(-0.1, 0.1)
    ),
    d_vectors=Gradient("vectors"),
)
class CharacterEmbed(Model):
    def __init__(self, nM=None, nC=None, **kwargs):
        Model.__init__(self, **kwargs)
        self.nM = nM
        self.nC = nC

    @property
    def nO(self):
        return self.nM * self.nC

    @property
    def nV(self):
        return 256

    def begin_update(self, docs, drop=0.0):
        if not docs:
            return []
        ids = []
        output = []
        weights = self.vectors
        # This assists in indexing; it's like looping over this dimension.
        # Still consider this weird witch craft...But thanks to Mark Neumann
        # for the tip.
        nCv = self.ops.xp.arange(self.nC)
        for doc in docs:
            doc_ids = doc.to_utf8_array(nr_char=self.nC)
            doc_vectors = self.ops.allocate((len(doc), self.nC, self.nM))
            # Let's say I have a 2d array of indices, and a 3d table of data. What numpy
            # incantation do I chant to get
            # output[i, j, k] == data[j, ids[i, j], k]?
            doc_vectors[:, nCv] = weights[nCv, doc_ids[:, nCv]]
            output.append(doc_vectors.reshape((len(doc), self.nO)))
            ids.append(doc_ids)

        def backprop_character_embed(d_vectors, sgd=None):
            gradient = self.d_vectors
            for doc_ids, d_doc_vectors in zip(ids, d_vectors):
                d_doc_vectors = d_doc_vectors.reshape((len(doc_ids), self.nC, self.nM))
                gradient[nCv, doc_ids[:, nCv]] += d_doc_vectors[:, nCv]
            if sgd is not None:
                sgd(self._mem.weights, self._mem.gradient, key=self.id)
            return None

        return output, backprop_character_embed


def PyTorchBiLSTM(nO, nI, depth, dropout=0.2):
    import torch.nn
    from thinc.extra.wrappers import PyTorchWrapperRNN

    if depth == 0:
        return layerize(noop())
    model = torch.nn.LSTM(nI, nO // 2, depth, bidirectional=True, dropout=dropout)
    return with_square_sequences(PyTorchWrapperRNN(model))

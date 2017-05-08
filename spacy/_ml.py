from thinc.api import add, layerize, chain, clone, concatenate, with_flatten
from thinc.neural import Model, Maxout, Softmax, Affine
from thinc.neural._classes.hash_embed import HashEmbed

from thinc.neural._classes.convolution import ExtractWindow
from thinc.neural._classes.static_vectors import StaticVectors
from thinc.neural._classes.batchnorm import BatchNorm
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


def get_col(idx):
    def forward(X, drop=0.):
        assert len(X.shape) <= 3
        output = Model.ops.xp.ascontiguousarray(X[:, idx])
        def backward(y, sgd=None):
            dX = Model.ops.allocate(X.shape)
            dX[:, idx] += y
            return dX
        return output, backward
    return layerize(forward)


def build_tok2vec(lang, width, depth=2, embed_size=1000):
    cols = [ID, LOWER, PREFIX, SUFFIX, SHAPE, TAG]
    with Model.define_operators({'>>': chain, '|': concatenate, '**': clone}):
        #static = get_col(cols.index(ID))     >> StaticVectors(lang, width)
        lower = get_col(cols.index(LOWER))     >> HashEmbed(width, embed_size)
        prefix = get_col(cols.index(PREFIX)) >> HashEmbed(width//4, embed_size)
        suffix = get_col(cols.index(SUFFIX)) >> HashEmbed(width//4, embed_size)
        shape = get_col(cols.index(SHAPE))   >> HashEmbed(width//4, embed_size)
        tag = get_col(cols.index(TAG))   >> HashEmbed(width//2, embed_size)
        tok2vec = (
            doc2feats(cols)
            >> with_flatten(
                #(static | prefix | suffix | shape)
                (lower | prefix | suffix | shape | tag)
                >> Maxout(width)
                >> (ExtractWindow(nW=1) >> Maxout(width, width*3))
                >> (ExtractWindow(nW=1) >> Maxout(width, width*3))
            )
        )
    return tok2vec


def doc2feats(cols):
    def forward(docs, drop=0.):
        feats = [doc.to_array(cols) for doc in docs]
        feats = [model.ops.asarray(f, dtype='uint64') for f in feats]
        return feats, None
    model = layerize(forward)
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
    ops = Model.ops
    def finish_update(d_X, sgd=None):
        return d_X
    X = ops.xp.concatenate([ops.asarray(seq) for seq in seqs])
    return X, finish_update



#def build_feature_precomputer(model, feat_maps):
#    '''Allow a model to be "primed" by pre-computing input features in bulk.
#
#    This is used for the parser, where we want to take a batch of documents,
#    and compute vectors for each (token, position) pair. These vectors can then
#    be reused, especially for beam-search.
#
#    Let's say we're using 12 features for each state, e.g. word at start of
#    buffer, three words on stack, their children, etc. In the normal arc-eager
#    system, a document of length N is processed in 2*N states. This means we'll
#    create 2*N*12 feature vectors --- but if we pre-compute, we only need
#    N*12 vector computations. The saving for beam-search is much better:
#    if we have a beam of k, we'll normally make 2*N*12*K computations -- 
#    so we can save the factor k. This also gives a nice CPU/GPU division:
#    we can do all our hard maths up front, packed into large multiplications,
#    and do the hard-to-program parsing on the CPU.
#    '''
#    def precompute(input_vectors):
#        cached, backprops = zip(*[lyr.begin_update(input_vectors)
#                                for lyr in feat_maps)
#        def forward(batch_token_ids, drop=0.):
#            output = ops.allocate((batch_size, output_width))
#            # i: batch index
#            # j: position index (i.e. N0, S0, etc
#            # tok_i: Index of the token within its document
#            for i, token_ids in enumerate(batch_token_ids):
#                for j, tok_i in enumerate(token_ids):
#                    output[i] += cached[j][tok_i]
#            def backward(d_vector, sgd=None):
#                d_inputs = ops.allocate((batch_size, n_feat, vec_width))
#                for i, token_ids in enumerate(batch_token_ids):
#                    for j in range(len(token_ids)):
#                        d_inputs[i][j] = backprops[j](d_vector, sgd)
#                # Return the IDs, so caller can associate to correct token
#                return (batch_token_ids, d_inputs)
#            return vector, backward
#        return chain(layerize(forward), model)
#    return precompute
#
#


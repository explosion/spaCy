from thinc.api import layerize, chain, clone, concatenate, with_flatten
from thinc.neural import Model, Maxout, Softmax
from thinc.neural._classes.hash_embed import HashEmbed

from thinc.neural._classes.convolution import ExtractWindow
from thinc.neural._classes.static_vectors import StaticVectors

from .attrs import ID, PREFIX, SUFFIX, SHAPE, TAG, DEP


def get_col(idx):
    def forward(X, drop=0.):
        output = Model.ops.xp.ascontiguousarray(X[:, idx])
        return output, None
    return layerize(forward)


def build_model(state2vec, width, depth, nr_class):
    with Model.define_operators({'>>': chain, '**': clone}):
        model = (
            state2vec
            >> Maxout(width, 1344)
            >> Maxout(width, width)
            >> Softmax(nr_class, width)
        )
    return model


def build_parser_state2vec(width, nr_vector=1000, nF=1, nB=0, nS=1, nL=2, nR=2):
    embed_tags = _reshape(chain(get_col(0), HashEmbed(16, nr_vector)))
    embed_deps = _reshape(chain(get_col(1), HashEmbed(16, nr_vector)))
    ops = embed_tags.ops
    def forward(tokens_attrs_vectors, drop=0.):
        tokens, attr_vals, tokvecs = tokens_attrs_vectors
        tagvecs, bp_tagvecs = embed_deps.begin_update(attr_vals, drop=drop)
        depvecs, bp_depvecs = embed_tags.begin_update(attr_vals, drop=drop)
        orig_tokvecs_shape = tokvecs.shape
        tokvecs = tokvecs.reshape((tokvecs.shape[0], tokvecs.shape[1] *
                                   tokvecs.shape[2]))

        shapes = (tagvecs.shape, depvecs.shape, tokvecs.shape)
        assert tagvecs.shape[0] == depvecs.shape[0] == tokvecs.shape[0], shapes
        vector = ops.xp.hstack((tagvecs, depvecs, tokvecs))

        def backward(d_vector, sgd=None):
            d_tagvecs, d_depvecs, d_tokvecs = backprop_concatenate(d_vector, shapes)
            assert d_tagvecs.shape == shapes[0], (d_tagvecs.shape, shapes)
            assert d_depvecs.shape == shapes[1], (d_depvecs.shape, shapes)
            assert d_tokvecs.shape == shapes[2], (d_tokvecs.shape, shapes)
            bp_tagvecs(d_tagvecs)
            bp_depvecs(d_depvecs)
            d_tokvecs = d_tokvecs.reshape(orig_tokvecs_shape)

            return (tokens, d_tokvecs)
        return vector, backward
    model = layerize(forward)
    model._layers = [embed_tags, embed_deps]
    return model


def backprop_concatenate(gradient, shapes):
    grads = []
    start = 0
    for shape in shapes:
        end = start + shape[1]
        grads.append(gradient[:, start : end])
        start = end
    return grads


def _reshape(layer):
    '''Transforms input with shape
      (states, tokens, features)
    into input with shape:
      (states * tokens, features)
    So that it can be used with a token-wise feature extraction layer, e.g.
    an embedding layer. The embedding layer outputs:
      (states * tokens, ndim)
    But we want to concatenate the vectors for the tokens, so we produce:
      (states, tokens * ndim)
    We then need to reverse the transforms to do the backward pass. Recall
    the simple rule here: each layer is a map:
        inputs -> (outputs, (d_outputs->d_inputs))
    So the shapes must match like this:
        shape of forward input == shape of backward output
        shape of backward input == shape of forward output
    '''
    def forward(X__bfm, drop=0.):
        b, f, m = X__bfm.shape
        B = b*f
        M = f*m
        X__Bm = X__bfm.reshape((B, m))
        y__Bn, bp_yBn = layer.begin_update(X__Bm, drop=drop)
        n = y__Bn.shape[1]
        N = f * n
        y__bN = y__Bn.reshape((b, N))
        def backward(dy__bN, sgd=None):
            dy__Bn = dy__bN.reshape((B, n))
            dX__Bm = bp_yBn(dy__Bn, sgd)
            if dX__Bm is None:
                return None
            else:
                return dX__Bm.reshape((b, f, m))
        return y__bN, backward
    model = layerize(forward)
    model._layers.append(layer)
    return model


@layerize
def flatten(seqs, drop=0.):
    ops = Model.ops
    def finish_update(d_X, sgd=None):
        return d_X
    X = ops.xp.concatenate([ops.asarray(seq) for seq in seqs])
    return X, finish_update


def build_tok2vec(lang, width, depth=2, embed_size=1000):
    cols = [ID, PREFIX, SUFFIX, SHAPE]
    with Model.define_operators({'>>': chain, '|': concatenate, '**': clone}):
        #static = get_col(cols.index(ID))     >> StaticVectors(lang, width)
        lower = get_col(cols.index(ID))     >> HashEmbed(width, embed_size)
        prefix = get_col(cols.index(PREFIX)) >> HashEmbed(width, embed_size)
        suffix = get_col(cols.index(SUFFIX)) >> HashEmbed(width, embed_size)
        shape = get_col(cols.index(SHAPE))   >> HashEmbed(width, embed_size)
        tok2vec = (
            doc2feats(cols)
            >> with_flatten(
                #(static | prefix | suffix | shape)
                (lower | prefix | suffix | shape)
                >> Maxout(width, width*4)
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

from thinc.api import layerize, chain, clone, concatenate, add
from thinc.neural import Model, Maxout, Softmax
from thinc.neural._classes.static_vectors import StaticVectors
from thinc.neural._classes.hash_embed import HashEmbed
from thinc.neural._classes.convolution import ExtractWindow


def get_col(idx):
    def forward(X, drop=0.):
        return Model.ops.xp.ascontiguousarray(X[:, idx]), None
    return layerize(forward)


def build_model(state2vec, width, depth, nr_class):
    with Model.define_operators({'>>': chain, '**': clone}):
        model = state2vec >> Maxout(width) ** depth >> Softmax(nr_class)
    return model


def build_parser_state2vec(tag_vectors, dep_vectors, **cfg):
    embed_tags = _reshape(chain(get_col(0), tag_vectors))
    embed_deps = _reshape(chain(get_col(1), dep_vectors))
    attr_names = ops.asarray([TAG, DEP], dtype='i')
    def forward(states, drop=0.):
        n_tokens = state.nr_context_tokens(nF, nB, nS, nL, nR)
        for i, state in enumerate(states):
            state.set_context_tokens(tokens[i], nF, nB, nS, nL, nR)
            state.set_attributes(features[i], tokens[i], attr_names)
            state.set_token_vectors(token_vectors[i], tokens[i])
        
        tagvecs, bp_tag_vecs = embed_deps.begin_update(attr_vals, drop=drop)
        depvecs, bp_dep_vecs = embed_tags.begin_update(attr_vals, drop=drop)

        vector = ops.concatenate((tagvecs, depvecs, tokvecs))

        shapes = (tagvecs.shape, depvecs.shape, tokvecs.shape)
        def backward(d_vector, sgd=None):
            d_depvecs, d_tagvecs, d_tokvecs = ops.backprop_concatenate(d_vector, shapes)
            bp_tagvecs(d_tagvecs)
            bp_depvecs(d_depvecs)
            return (d_tokvecs, tokens)
        return vector, backward
    model = layerize(forward)
    model._layers = [embed_tags, embed_deps]
    return model


def _reshape(layer):
    def forward(X, drop=0.):
        Xh = X.reshape((X.shape[0] * X.shape[1], X.shape[2]))
        yh, bp_yh = layer.begin_update(Xh, drop=drop)
        n = X.shape[0]
        def backward(d_y, sgd=None):
            d_yh = d_y.reshape((n, d_y.size / n))
            d_Xh = bp_yh(d_yh, sgd)
            return d_Xh.reshape(old_shape)
        return yh.reshape((n, yh.shape / n)), backward
    model = layerize(forward)
    model._layers.append(layer)
    return model



#def build_tok2vec(lang, width, depth, embed_size, cols):
#    with Model.define_operators({'>>': chain, '|': concatenate, '**': clone}):
#        static = get_col(cols.index(ID))     >> StaticVectors(lang, width)
#        prefix = get_col(cols.index(PREFIX)) >> HashEmbed(width, embed_size)
#        suffix = get_col(cols.index(SUFFIX)) >> HashEmbed(width, embed_size)
#        shape = get_col(cols.index(SHAPE))   >> HashEmbed(width, embed_size)
#        tok2vec = (
#            (static | prefix | suffix | shape)
#            >> Maxout(width, width*4)
#            >> (ExtractWindow(nW=1) >> Maxout(width, width*3)) ** depth
#        )
#    return tok2vec


if __name__ == '__main__':
    test_build_model()

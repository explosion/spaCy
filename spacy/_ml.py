from thinc.api import layerize, chain, clone
from thinc.neural import Model, Maxout, Softmax
from thinc.neural._classes.hash_embed import HashEmbed
from .attrs import TAG, DEP


def get_col(idx):
    def forward(X, drop=0.):
        return Model.ops.xp.ascontiguousarray(X[:, idx]), None
    return layerize(forward)


def build_model(state2vec, width, depth, nr_class):
    with Model.define_operators({'>>': chain, '**': clone}):
        model = state2vec >> Maxout(width) ** depth >> Softmax(nr_class)
    return model


def build_parser_state2vec(width, nr_vector=1000, nF=1, nB=0, nS=1, nL=2, nR=2):
    embed_tags = _reshape(chain(get_col(0), HashEmbed(width, nr_vector)))
    embed_deps = _reshape(chain(get_col(1), HashEmbed(width, nr_vector)))
    ops = embed_tags.ops
    attr_names = ops.asarray([TAG, DEP], dtype='i')
    extract = build_feature_extractor(attr_names, nF, nB, nS, nL, nR)
    def forward(states, drop=0.):
        tokens, attr_vals, tokvecs = extract(states)
        tagvecs, bp_tagvecs = embed_deps.begin_update(attr_vals, drop=drop)
        depvecs, bp_depvecs = embed_tags.begin_update(attr_vals, drop=drop)

        tokvecs = tokvecs.reshape((tokvecs.shape[0], tokvecs.shape[1] *
                                   tokvecs.shape[2]))

        vector = ops.concatenate((tagvecs, depvecs, tokvecs))

        shapes = (tagvecs.shape, depvecs.shape, tokvecs.shape)
        def backward(d_vector, sgd=None):
            d_depvecs, d_tagvecs, d_tokvecs = ops.backprop_concatenate(d_vector, shapes)
            bp_tagvecs(d_tagvecs)
            bp_depvecs(d_depvecs)
            d_tokvecs = d_tokvecs.reshape((len(states), tokens.shape[1], tokvecs.shape[2]))
            return (d_tokvecs, tokens)
        return vector, backward
    model = layerize(forward)
    model._layers = [embed_tags, embed_deps]
    return model


def build_feature_extractor(attr_names, nF, nB, nS, nL, nR):
    def forward(states, drop=0.):
        ops = model.ops
        n_tokens = states[0].nr_context_tokens(nF, nB, nS, nL, nR)
        vector_length = states[0].token_vector_length
        tokens = ops.allocate((len(states), n_tokens), dtype='i')
        features = ops.allocate((len(states), n_tokens, attr_names.shape[0]), dtype='i')
        tokvecs = ops.allocate((len(states), n_tokens, vector_length), dtype='f')
        for i, state in enumerate(states):
            state.set_context_tokens(tokens[i], nF, nB, nS, nL, nR)
            state.set_attributes(features[i], tokens[i], attr_names)
            state.set_token_vectors(tokvecs[i], tokens[i])
        def backward(d_features, sgd=None):
            return d_features
        return (tokens, features, tokvecs), backward
    model = layerize(forward)
    return model


def _reshape(layer):
    def forward(X, drop=0.):
        Xh = X.reshape((X.shape[0] * X.shape[1], X.shape[2]))
        yh, bp_yh = layer.begin_update(Xh, drop=drop)
        n = X.shape[0]
        old_shape = X.shape
        def backward(d_y, sgd=None):
            d_yh = d_y.reshape((n, d_y.size / n))
            d_Xh = bp_yh(d_yh, sgd)
            return d_Xh.reshape(old_shape)
        return yh.reshape((n, yh.shape / n)), backward
    model = layerize(forward)
    model._layers.append(layer)
    return model

#from thinc.api import layerize, chain, clone, concatenate, add
# from thinc.neural._classes.convolution import ExtractWindow
# from thinc.neural._classes.static_vectors import StaticVectors

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

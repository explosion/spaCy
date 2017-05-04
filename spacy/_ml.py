from thinc.api import layerize, chain, clone, concatenate, add
from thinc.neural import Model, Maxout, Softmax
from thinc.neural._classes.static_vectors import StaticVectors
from thinc.neural._classes.hash_embed import HashEmbed
from thinc.neural._classes.convolution import ExtractWindow

from .attrs import ID, PREFIX, SUFFIX, SHAPE, TAG, DEP


@layerize
def get_contexts(states, drop=0.):
    ops = Model.ops
    context = ops.allocate((len(states), 7), dtype='uint64')
    for i, state in enumerate(states):
        context[i, 0] = state.B(0)
        context[i, 1] = state.S(0)
        context[i, 2] = state.S(1)
        context[i, 3] = state.L(state.S(0), 1)
        context[i, 4] = state.L(state.S(0), 2)
        context[i, 5] = state.R(state.S(0), 1)
        context[i, 6] = state.R(state.S(0), 2)
    return (context, states), None

def get_col(idx):
    def forward(X, drop=0.):
        return Model.ops.xp.ascontiguousarray(X[:, idx]), None
    return layerize(forward)


def extract_features(attrs):
    ops = Model.ops
    def forward(contexts_states, drop=0.):
        contexts, states = contexts_states
        output = ops.allocate((len(states), contexts.shape[1], len(attrs)),
                              dtype='uint64')
        for i, state in enumerate(states):
            for j, tok_i in enumerate(contexts[i]):
                token = state.get_token(tok_i)
                for k, attr in enumerate(attrs):
                    output[i, j, k] = getattr(token, attr)
        return output, None
    return layerize(forward)


def build_tok2vec(lang, width, depth, embed_size):
    cols = [ID, PREFIX, SUFFIX, SHAPE]
    
    with Model.define_operators({'>>': chain, '|': concatenate, '**': clone}):
        static = get_col(cols.index(ID))     >> StaticVectors('en', width)
        prefix = get_col(cols.index(PREFIX)) >> HashEmbed(width, embed_size)
        suffix = get_col(cols.index(SUFFIX)) >> HashEmbed(width, embed_size)
        shape = get_col(cols.index(SHAPE))   >> HashEmbed(width, embed_size)
        tok2vec = (
            extract_features(cols)
            >> (static | prefix | suffix | shape)
            >> (ExtractWindow(nW=1) >> Maxout(width)) ** depth
        )
    return tok2vec


def build_parse2vec(width, embed_size):
    cols = [TAG, DEP]
    with Model.define_operators({'>>': chain, '|': concatenate}):
        tag_vector = get_col(cols.index(TAG)) >> HashEmbed(width, 1000)
        dep_vector = get_col(cols.index(DEP)) >> HashEmbed(width, 1000)
        model = (
            extract_features([TAG, DEP])
            >> (tag_vector | dep_vector)
        )
    return model
 

def build_model(state2context, tok2vec, parse2vec, width, depth, nr_class):
    with Model.define_operators({'>>': chain, '**': clone, '|': concatenate}):
        model = (
            state2context
            >> (tok2vec | parse2vec)
            >> Maxout(width) ** depth
            >> Softmax(nr_class)
        )
    return model


def test_build_model(width=100, depth=2, nr_class=10):
    model = build_model(
                get_contexts,
                build_tok2vec('en', width=100, depth=2, embed_size=1000),
                build_parse2vec(width=100, embed_size=1000),
                width,
                depth,
                nr_class)
    assert model is not None


if __name__ == '__main__':
    test_build_model()

import pytest
from thinc.api import NumpyOps, fix_random_seed, Adam, set_dropout_rate
from numpy.testing import assert_array_equal
import numpy

from spacy.ml.models.tok2vec import build_Tok2Vec_model
from spacy.lang.en import English
from spacy.lang.en.examples import sentences as EN_SENTENCES


def get_all_params(model):
    params = []
    for node in model.walk():
        for name in node.param_names:
            params.append(node.get_param(name).ravel())
    return node.ops.xp.concatenate(params)


def get_docs():
    nlp = English()
    return list(nlp.pipe(EN_SENTENCES + [" ".join(EN_SENTENCES)]))


def get_gradient(model, Y):
    if isinstance(Y, model.ops.xp.ndarray):
        dY = model.ops.alloc(Y.shape, dtype=Y.dtype)
        dY += model.ops.xp.random.uniform(-1., 1., Y.shape)
        return dY
    else:
        return [get_gradient(model, y) for y in Y]


TOK2VEC_KWARGS = {
    "width": 96,
    "embed_size": 2000,
    "subword_features": True,
    "char_embed": False,
    "conv_depth": 4,
    "bilstm_depth": 0,
    "maxout_pieces": 4,
    "window_size": 1,
    "dropout": 0.1,
    "nM": 0,
    "nC": 0,
    "pretrained_vectors": None,
}
@pytest.mark.parametrize("seed,model_func,kwargs", [ # TODO: Test more models.
    (0, build_Tok2Vec_model, TOK2VEC_KWARGS),
])
def test_models_initialize_consistently(seed, model_func, kwargs):
    fix_random_seed(seed)
    model1 = model_func(**kwargs)
    model1.initialize()
    fix_random_seed(seed)
    model2 = model_func(**kwargs)
    model2.initialize()
    params1 = get_all_params(model1)
    params2 = get_all_params(model2)
    assert_array_equal(params1, params2)
    

@pytest.mark.parametrize("seed,model_func,kwargs,get_X", [ # TODO: Test more models.
    (0, build_Tok2Vec_model, TOK2VEC_KWARGS, get_docs),
])
def test_models_predict_consistently(seed, model_func, kwargs, get_X):
    fix_random_seed(seed)
    model1 = model_func(**kwargs).initialize()
    Y1 = model1.predict(get_X())
    fix_random_seed(seed)
    model2 = model_func(**kwargs).initialize()
    Y2 = model2.predict(get_X())

    if isinstance(Y1, numpy.ndarray):
        assert_array_equal(Y1, Y2)
    else:
        assert len(Y1) == len(Y2)
        for y1, y2 in zip(Y1, Y2):
            assert_array_equal(y1, y2)


@pytest.mark.parametrize("seed,dropout,model_func,kwargs,get_X", [ # TODO: Test more models.
    (0, 0.2, build_Tok2Vec_model, TOK2VEC_KWARGS, get_docs),
])
def test_models_update_consistently(seed, dropout, model_func, kwargs, get_X):
    def get_updated_model():
        fix_random_seed(seed)
        optimizer = Adam(0.001)
        model = model_func(**kwargs).initialize()
        initial_params = get_all_params(model)
        set_dropout_rate(model, dropout)
        for _ in range(5):
            Y, get_dX = model.begin_update(get_X())
            dY = get_gradient(model, Y)
            _ = get_dX(dY)
            model.finish_update(optimizer)
        updated_params = get_all_params(model)
        with pytest.raises(AssertionError):
            assert_array_equal(initial_params, updated_params)
        return model

    model1 = get_updated_model()
    model2 = get_updated_model()

    assert_array_equal(get_all_params(model1), get_all_params(model2))

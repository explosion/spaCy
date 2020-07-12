from typing import List

import pytest
from thinc.api import fix_random_seed, Adam, set_dropout_rate
from numpy.testing import assert_array_equal
import numpy

from spacy.ml.models import build_Tok2Vec_model
from spacy.ml.models import build_text_classifier, build_simple_cnn_text_classifier
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
        dY += model.ops.xp.random.uniform(-1.0, 1.0, Y.shape)
        return dY
    elif isinstance(Y, List):
        return [get_gradient(model, y) for y in Y]
    else:
        raise ValueError(f"Could not get gradient for type {type(Y)}")


def default_tok2vec():
    return build_Tok2Vec_model(**TOK2VEC_KWARGS)


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

TEXTCAT_KWARGS = {
    "width": 64,
    "embed_size": 2000,
    "pretrained_vectors": None,
    "exclusive_classes": False,
    "ngram_size": 1,
    "window_size": 1,
    "conv_depth": 2,
    "dropout": None,
    "nO": 7
}

TEXTCAT_CNN_KWARGS = {
    "tok2vec": default_tok2vec(),
    "exclusive_classes": False,
    "nO": 13,
}


@pytest.mark.parametrize(
    "seed,model_func,kwargs",
    [
        (0, build_Tok2Vec_model, TOK2VEC_KWARGS),
        (0, build_text_classifier, TEXTCAT_KWARGS),
        (0, build_simple_cnn_text_classifier, TEXTCAT_CNN_KWARGS),
    ],
)
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


@pytest.mark.parametrize(
    "seed,model_func,kwargs,get_X",
    [
        (0, build_Tok2Vec_model, TOK2VEC_KWARGS, get_docs),
        (0, build_text_classifier, TEXTCAT_KWARGS, get_docs),
        (0, build_simple_cnn_text_classifier, TEXTCAT_CNN_KWARGS, get_docs),
    ],
)
def test_models_predict_consistently(seed, model_func, kwargs, get_X):
    fix_random_seed(seed)
    model1 = model_func(**kwargs).initialize()
    Y1 = model1.predict(get_X())
    fix_random_seed(seed)
    model2 = model_func(**kwargs).initialize()
    Y2 = model2.predict(get_X())

    if model1.has_ref("tok2vec"):
        tok2vec1 = model1.get_ref("tok2vec").predict(get_X())
        tok2vec2 = model2.get_ref("tok2vec").predict(get_X())
        for i in range(len(tok2vec1)):
            for j in range(len(tok2vec1[i])):
                assert_array_equal(numpy.asarray(tok2vec1[i][j]), numpy.asarray(tok2vec2[i][j]))

    if isinstance(Y1, numpy.ndarray):
        assert_array_equal(Y1, Y2)
    elif isinstance(Y1, List):
        assert len(Y1) == len(Y2)
        for y1, y2 in zip(Y1, Y2):
            assert_array_equal(y1, y2)
    else:
        raise ValueError(f"Could not compare type {type(Y1)}")


@pytest.mark.parametrize(
    "seed,dropout,model_func,kwargs,get_X",
    [
        (0, 0.2, build_Tok2Vec_model, TOK2VEC_KWARGS, get_docs),
        (0, 0.2, build_text_classifier, TEXTCAT_KWARGS, get_docs),
        (0, 0.2, build_simple_cnn_text_classifier, TEXTCAT_CNN_KWARGS, get_docs),
    ],
)
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

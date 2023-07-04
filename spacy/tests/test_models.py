from typing import List

import numpy
import pytest
from numpy.testing import assert_array_almost_equal, assert_array_equal
from thinc.api import (
    Adam,
    Logistic,
    Ragged,
    Relu,
    chain,
    fix_random_seed,
    reduce_mean,
    set_dropout_rate,
)

from spacy.lang.en import English
from spacy.lang.en.examples import sentences as EN_SENTENCES
from spacy.ml.extract_spans import _get_span_indices, extract_spans
from spacy.ml.models import (
    MaxoutWindowEncoder,
    MultiHashEmbed,
    build_bow_text_classifier,
    build_simple_cnn_text_classifier,
    build_spancat_model,
    build_Tok2Vec_model,
)
from spacy.ml.staticvectors import StaticVectors


def get_textcat_bow_kwargs():
    return {
        "exclusive_classes": True,
        "ngram_size": 1,
        "no_output_layer": False,
        "nO": 34,
    }


def get_textcat_cnn_kwargs():
    return {"tok2vec": make_test_tok2vec(), "exclusive_classes": False, "nO": 13}


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


def get_tok2vec_kwargs():
    # This actually creates models, so seems best to put it in a function.
    return {
        "embed": MultiHashEmbed(
            width=32,
            rows=[500, 500, 500],
            attrs=["NORM", "PREFIX", "SHAPE"],
            include_static_vectors=False,
        ),
        "encode": MaxoutWindowEncoder(
            width=32, depth=2, maxout_pieces=2, window_size=1
        ),
    }


def make_test_tok2vec():
    return build_Tok2Vec_model(**get_tok2vec_kwargs())


def test_multi_hash_embed():
    embed = MultiHashEmbed(
        width=32,
        rows=[500, 500, 500],
        attrs=["NORM", "PREFIX", "SHAPE"],
        include_static_vectors=False,
    )
    hash_embeds = [node for node in embed.walk() if node.name == "hashembed"]
    assert len(hash_embeds) == 3
    # Check they look at different columns.
    assert list(sorted(he.attrs["column"] for he in hash_embeds)) == [0, 1, 2]
    # Check they use different seeds
    assert len(set(he.attrs["seed"] for he in hash_embeds)) == 3
    # Check they all have the same number of rows
    assert [he.get_dim("nV") for he in hash_embeds] == [500, 500, 500]
    # Now try with different row factors
    embed = MultiHashEmbed(
        width=32,
        rows=[1000, 50, 250],
        attrs=["NORM", "PREFIX", "SHAPE"],
        include_static_vectors=False,
    )
    hash_embeds = [node for node in embed.walk() if node.name == "hashembed"]
    assert [he.get_dim("nV") for he in hash_embeds] == [1000, 50, 250]


@pytest.mark.parametrize(
    "seed,model_func,kwargs",
    [
        (0, build_Tok2Vec_model, get_tok2vec_kwargs()),
        (0, build_bow_text_classifier, get_textcat_bow_kwargs()),
        (0, build_simple_cnn_text_classifier, get_textcat_cnn_kwargs()),
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
    assert_array_equal(model1.ops.to_numpy(params1), model2.ops.to_numpy(params2))


@pytest.mark.parametrize(
    "seed,model_func,kwargs,get_X",
    [
        (0, build_Tok2Vec_model, get_tok2vec_kwargs(), get_docs),
        (0, build_bow_text_classifier, get_textcat_bow_kwargs(), get_docs),
        (0, build_simple_cnn_text_classifier, get_textcat_cnn_kwargs(), get_docs),
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
                assert_array_equal(
                    numpy.asarray(model1.ops.to_numpy(tok2vec1[i][j])),
                    numpy.asarray(model2.ops.to_numpy(tok2vec2[i][j])),
                )

    try:
        Y1 = model1.ops.to_numpy(Y1)
        Y2 = model2.ops.to_numpy(Y2)
    except Exception:
        pass
    if isinstance(Y1, numpy.ndarray):
        assert_array_equal(Y1, Y2)
    elif isinstance(Y1, List):
        assert len(Y1) == len(Y2)
        for y1, y2 in zip(Y1, Y2):
            try:
                y1 = model1.ops.to_numpy(y1)
                y2 = model2.ops.to_numpy(y2)
            except Exception:
                pass
            assert_array_equal(y1, y2)
    else:
        raise ValueError(f"Could not compare type {type(Y1)}")


@pytest.mark.parametrize(
    "seed,dropout,model_func,kwargs,get_X",
    [
        (0, 0.2, build_Tok2Vec_model, get_tok2vec_kwargs(), get_docs),
        (0, 0.2, build_bow_text_classifier, get_textcat_bow_kwargs(), get_docs),
        (0, 0.2, build_simple_cnn_text_classifier, get_textcat_cnn_kwargs(), get_docs),
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
            get_dX(dY)
            model.finish_update(optimizer)
        updated_params = get_all_params(model)
        with pytest.raises(AssertionError):
            assert_array_equal(
                model.ops.to_numpy(initial_params), model.ops.to_numpy(updated_params)
            )
        return model

    model1 = get_updated_model()
    model2 = get_updated_model()
    assert_array_almost_equal(
        model1.ops.to_numpy(get_all_params(model1)),
        model2.ops.to_numpy(get_all_params(model2)),
        decimal=5,
    )


@pytest.mark.parametrize("model_func,kwargs", [(StaticVectors, {"nO": 128, "nM": 300})])
def test_empty_docs(model_func, kwargs):
    nlp = English()
    model = model_func(**kwargs).initialize()
    # Test the layer can be called successfully with 0, 1 and 2 empty docs.
    for n_docs in range(3):
        docs = [nlp("") for _ in range(n_docs)]
        # Test predict
        model.predict(docs)
        # Test backprop
        output, backprop = model.begin_update(docs)
        backprop(output)


def test_init_extract_spans():
    extract_spans().initialize()


def test_extract_spans_span_indices():
    model = extract_spans().initialize()
    spans = Ragged(
        model.ops.asarray([[0, 3], [2, 3], [5, 7]], dtype="i"),
        model.ops.asarray([2, 1], dtype="i"),
    )
    x_lengths = model.ops.asarray([5, 10], dtype="i")
    indices = _get_span_indices(model.ops, spans, x_lengths)
    assert list(indices) == [0, 1, 2, 2, 10, 11]


def test_extract_spans_forward_backward():
    model = extract_spans().initialize()
    X = Ragged(model.ops.alloc2f(15, 4), model.ops.asarray([5, 10], dtype="i"))
    spans = Ragged(
        model.ops.asarray([[0, 3], [2, 3], [5, 7]], dtype="i"),
        model.ops.asarray([2, 1], dtype="i"),
    )
    Y, backprop = model.begin_update((X, spans))
    assert list(Y.lengths) == [3, 1, 2]
    assert Y.dataXd.shape == (6, 4)
    dX, spans2 = backprop(Y)
    assert spans2 is spans
    assert dX.dataXd.shape == X.dataXd.shape
    assert list(dX.lengths) == list(X.lengths)


def test_spancat_model_init():
    model = build_spancat_model(
        build_Tok2Vec_model(**get_tok2vec_kwargs()), reduce_mean(), Logistic()
    )
    model.initialize()


def test_spancat_model_forward_backward(nO=5):
    tok2vec = build_Tok2Vec_model(**get_tok2vec_kwargs())
    docs = get_docs()
    spans_list = []
    lengths = []
    for doc in docs:
        spans_list.append(doc[:2])
        spans_list.append(doc[1:4])
        lengths.append(2)
    spans = Ragged(
        tok2vec.ops.asarray([[s.start, s.end] for s in spans_list], dtype="i"),
        tok2vec.ops.asarray(lengths, dtype="i"),
    )
    model = build_spancat_model(
        tok2vec, reduce_mean(), chain(Relu(nO=nO), Logistic())
    ).initialize(X=(docs, spans))

    Y, backprop = model((docs, spans), is_train=True)
    assert Y.shape == (spans.dataXd.shape[0], nO)
    backprop(Y)

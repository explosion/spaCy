import pytest

from spacy import registry
from spacy.training import Example
from spacy.vocab import Vocab
from spacy.pipeline._parser_internals.arc_eager import ArcEager
from spacy.pipeline.transition_parser import Parser
from spacy.tokens.doc import Doc
from thinc.api import Model
from spacy.pipeline.tok2vec import DEFAULT_TOK2VEC_MODEL
from spacy.pipeline.dep_parser import DEFAULT_PARSER_MODEL


@pytest.fixture
def vocab():
    return Vocab()


@pytest.fixture
def arc_eager(vocab):
    actions = ArcEager.get_actions(left_labels=["L"], right_labels=["R"])
    return ArcEager(vocab.strings, actions)


@pytest.fixture
def tok2vec():
    cfg = {"model": DEFAULT_TOK2VEC_MODEL}
    tok2vec = registry.resolve(cfg, validate=True)["model"]
    tok2vec.initialize()
    return tok2vec


@pytest.fixture
def parser(vocab, arc_eager):
    config = {
        "learn_tokens": False,
        "min_action_freq": 30,
        "update_with_oracle_cut_size": 100,
    }
    cfg = {"model": DEFAULT_PARSER_MODEL}
    model = registry.resolve(cfg, validate=True)["model"]
    return Parser(vocab, model, moves=arc_eager, **config)


@pytest.fixture
def model(arc_eager, tok2vec, vocab):
    cfg = {"model": DEFAULT_PARSER_MODEL}
    model = registry.resolve(cfg, validate=True)["model"]
    model.attrs["resize_output"](model, arc_eager.n_moves)
    model.initialize()
    return model


@pytest.fixture
def doc(vocab):
    return Doc(vocab, words=["a", "b", "c"])


@pytest.fixture
def gold(doc):
    return {"heads": [1, 1, 1], "deps": ["L", "ROOT", "R"]}


def test_can_init_nn_parser(parser):
    assert isinstance(parser.model, Model)


def test_build_model(parser, vocab):
    config = {
        "learn_tokens": False,
        "min_action_freq": 0,
        "update_with_oracle_cut_size": 100,
    }
    cfg = {"model": DEFAULT_PARSER_MODEL}
    model = registry.resolve(cfg, validate=True)["model"]
    parser.model = Parser(vocab, model=model, moves=parser.moves, **config).model
    assert parser.model is not None


def test_predict_doc(parser, tok2vec, model, doc):
    doc.tensor = tok2vec.predict([doc])[0]
    parser.model = model
    parser(doc)


def test_update_doc(parser, model, doc, gold):
    parser.model = model

    def optimize(key, weights, gradient):
        weights -= 0.001 * gradient
        return weights, gradient

    example = Example.from_dict(doc, gold)
    parser.update([example], sgd=optimize)


@pytest.mark.skip(reason="No longer supported")
def test_predict_doc_beam(parser, model, doc):
    parser.model = model
    parser(doc, beam_width=32, beam_density=0.001)


@pytest.mark.skip(reason="No longer supported")
def test_update_doc_beam(parser, model, doc, gold):
    parser.model = model

    def optimize(weights, gradient, key=None):
        weights -= 0.001 * gradient

    parser.update_beam((doc, gold), sgd=optimize)

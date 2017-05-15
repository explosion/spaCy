from thinc.neural import Model
from mock import Mock
import pytest
import numpy

from ..._ml import chain, Tok2Vec, doc2feats
from ...vocab import Vocab
from ...pipeline import TokenVectorEncoder
from ...syntax.arc_eager import ArcEager
from ...syntax.nn_parser import Parser
from ...tokens.doc import Doc
from ...gold import GoldParse


@pytest.fixture
def vocab():
    return Vocab()


@pytest.fixture
def arc_eager(vocab):
    actions = ArcEager.get_actions(left_labels=['L'], right_labels=['R'])
    return ArcEager(vocab.strings, actions)


@pytest.fixture
def tok2vec():
    return Tok2Vec(8, 100, preprocess=doc2feats())


@pytest.fixture
def parser(vocab, arc_eager):
    return Parser(vocab, moves=arc_eager, model=None)

@pytest.fixture
def model(arc_eager, tok2vec):
    return Parser.Model(arc_eager.n_moves, tok2vec)

@pytest.fixture
def doc(vocab):
    return Doc(vocab, words=['a', 'b', 'c'])

@pytest.fixture
def gold(doc):
    return GoldParse(doc, heads=[1, 1, 1], deps=['L', 'ROOT', 'R'])
def test_can_init_nn_parser(parser):
    assert parser.model is None


def test_build_model(parser, tok2vec):
    parser.model = Parser.Model(parser.moves.n_moves, tok2vec)
    assert parser.model is not None


def test_predict_doc(parser, model, doc):
    parser.model = model
    parser(doc)


def test_update_doc(parser, model, doc, gold):
    parser.model = model
    loss1 = parser.update(doc, gold)
    assert loss1 > 0
    loss2 = parser.update(doc, gold)
    assert loss2 == loss1
    def optimize(weights, gradient, key=None):
        weights -= 0.001 * gradient
    loss3 = parser.update(doc, gold, sgd=optimize)
    loss4 = parser.update(doc, gold, sgd=optimize)
    assert loss3 < loss2

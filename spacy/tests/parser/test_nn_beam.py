from __future__ import unicode_literals
import pytest
import numpy
from thinc.api import layerize

from ...vocab import Vocab
from ...syntax.arc_eager import ArcEager
from ...tokens import Doc
from ...gold import GoldParse
from ...syntax._beam_utils import ParserBeam, update_beam


@pytest.fixture
def vocab():
    return Vocab()

@pytest.fixture
def moves(vocab):
    aeager = ArcEager(vocab.strings, {})
    aeager.add_action(2, 'nsubj')
    aeager.add_action(3, 'dobj')
    aeager.add_action(2, 'aux')
    return aeager


@pytest.fixture
def docs(vocab):
    return [Doc(vocab, words=['Rats', 'bite', 'things'])]

@pytest.fixture
def tokvecs(docs, vector_size):
    output = []
    for doc in docs:
        vec = numpy.random.uniform(-0.1, 0.1, (len(doc), vector_size))
        output.append(numpy.asarray(vec))
    return output


@pytest.fixture
def golds(docs):
    return [GoldParse(doc) for doc in docs]


@pytest.fixture
def batch_size(docs):
    return len(docs)


@pytest.fixture
def beam_width():
    return 4


@pytest.fixture
def vector_size():
    return 6


@pytest.fixture
def beam(moves, docs, golds, beam_width):
    return ParserBeam(moves, docs, golds, width=beam_width)

@pytest.fixture
def scores(moves, batch_size, beam_width):
    return [
        numpy.asarray(
            numpy.random.uniform(-0.1, 0.1, (batch_size, moves.n_moves)),
            dtype='f')
        for _ in range(batch_size)]


def test_create_beam(beam):
    pass


def test_beam_advance(beam, scores):
    beam.advance(scores)


def test_beam_advance_too_few_scores(beam, scores):
    with pytest.raises(IndexError):
        beam.advance(scores[:-1])


def test_update_beam(moves, docs, tokvecs, golds, vector_size):
    @layerize
    def state2vec(X, drop=0.):
        vec = numpy.ones((X.shape[0], vector_size), dtype='f')
        return vec, None
    @layerize
    def vec2scores(X, drop=0.):
        scores = numpy.ones((X.shape[0], moves.n_moves), dtype='f')
        return scores, None
    d_loss, backprops = update_beam(moves, 13, docs, tokvecs, golds,
                            state2vec, vec2scores, drop=0.0, sgd=None,
                            losses={}, width=4, density=0.001)



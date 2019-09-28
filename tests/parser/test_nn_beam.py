# coding: utf8
from __future__ import unicode_literals

import pytest
import numpy
from spacy.vocab import Vocab
from spacy.language import Language
from spacy.pipeline import DependencyParser
from spacy.syntax.arc_eager import ArcEager
from spacy.tokens import Doc
from spacy.syntax._beam_utils import ParserBeam
from spacy.syntax.stateclass import StateClass
from spacy.gold import GoldParse


@pytest.fixture
def vocab():
    return Vocab()


@pytest.fixture
def moves(vocab):
    aeager = ArcEager(vocab.strings, {})
    aeager.add_action(2, "nsubj")
    aeager.add_action(3, "dobj")
    aeager.add_action(2, "aux")
    return aeager


@pytest.fixture
def docs(vocab):
    return [Doc(vocab, words=["Rats", "bite", "things"])]


@pytest.fixture
def states(docs):
    return [StateClass(doc) for doc in docs]


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
def beam(moves, states, golds, beam_width):
    return ParserBeam(moves, states, golds, width=beam_width, density=0.0)


@pytest.fixture
def scores(moves, batch_size, beam_width):
    return [
        numpy.asarray(
            numpy.random.uniform(-0.1, 0.1, (batch_size, moves.n_moves)), dtype="f"
        )
        for _ in range(batch_size)
    ]


def test_create_beam(beam):
    pass


def test_beam_advance(beam, scores):
    beam.advance(scores)


def test_beam_advance_too_few_scores(beam, scores):
    with pytest.raises(IndexError):
        beam.advance(scores[:-1])


def test_beam_parse():
    nlp = Language()
    nlp.add_pipe(DependencyParser(nlp.vocab), name="parser")
    nlp.parser.add_label("nsubj")
    nlp.parser.begin_training([], token_vector_width=8, hidden_width=8)
    doc = nlp.make_doc("Australia is a country")
    nlp.parser(doc, beam_width=2)

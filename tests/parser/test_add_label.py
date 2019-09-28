# coding: utf8
from __future__ import unicode_literals

import pytest
from thinc.neural.optimizers import Adam
from thinc.neural.ops import NumpyOps
from spacy.attrs import NORM
from spacy.gold import GoldParse
from spacy.vocab import Vocab
from spacy.tokens import Doc
from spacy.pipeline import DependencyParser, EntityRecognizer
from spacy.util import fix_random_seed


@pytest.fixture
def vocab():
    return Vocab(lex_attr_getters={NORM: lambda s: s})


@pytest.fixture
def parser(vocab):
    parser = DependencyParser(vocab)
    return parser


def test_init_parser(parser):
    pass


def _train_parser(parser):
    fix_random_seed(1)
    parser.add_label("left")
    parser.begin_training([], **parser.cfg)
    sgd = Adam(NumpyOps(), 0.001)

    for i in range(5):
        losses = {}
        doc = Doc(parser.vocab, words=["a", "b", "c", "d"])
        gold = GoldParse(doc, heads=[1, 1, 3, 3], deps=["left", "ROOT", "left", "ROOT"])
        parser.update([doc], [gold], sgd=sgd, losses=losses)
    return parser


def test_add_label(parser):
    parser = _train_parser(parser)
    parser.add_label("right")
    sgd = Adam(NumpyOps(), 0.001)
    for i in range(10):
        losses = {}
        doc = Doc(parser.vocab, words=["a", "b", "c", "d"])
        gold = GoldParse(
            doc, heads=[1, 1, 3, 3], deps=["right", "ROOT", "left", "ROOT"]
        )
        parser.update([doc], [gold], sgd=sgd, losses=losses)
    doc = Doc(parser.vocab, words=["a", "b", "c", "d"])
    doc = parser(doc)
    assert doc[0].dep_ == "right"
    assert doc[2].dep_ == "left"


def test_add_label_deserializes_correctly():
    ner1 = EntityRecognizer(Vocab())
    ner1.add_label("C")
    ner1.add_label("B")
    ner1.add_label("A")
    ner1.begin_training([])
    ner2 = EntityRecognizer(Vocab()).from_bytes(ner1.to_bytes())
    assert ner1.moves.n_moves == ner2.moves.n_moves
    for i in range(ner1.moves.n_moves):
        assert ner1.moves.get_class_name(i) == ner2.moves.get_class_name(i)


@pytest.mark.parametrize(
    "pipe_cls,n_moves", [(DependencyParser, 5), (EntityRecognizer, 4)]
)
def test_add_label_get_label(pipe_cls, n_moves):
    """Test that added labels are returned correctly. This test was added to
    test for a bug in DependencyParser.labels that'd cause it to fail when
    splitting the move names.
    """
    labels = ["A", "B", "C"]
    pipe = pipe_cls(Vocab())
    for label in labels:
        pipe.add_label(label)
    assert len(pipe.move_names) == len(labels) * n_moves
    pipe_labels = sorted(list(pipe.labels))
    assert pipe_labels == labels

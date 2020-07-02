import pytest
from thinc.api import Adam
from spacy.attrs import NORM
from spacy.vocab import Vocab

from spacy.gold import Example
from spacy.pipeline.defaults import default_parser
from spacy.tokens import Doc
from spacy.pipeline import DependencyParser


@pytest.fixture
def vocab():
    return Vocab(lex_attr_getters={NORM: lambda s: s})


@pytest.fixture
def parser(vocab):
    config = {
        "learn_tokens": False,
        "min_action_freq": 30,
        "beam_width": 1,
        "beam_update_prob": 1.0,
    }
    parser = DependencyParser(vocab, default_parser(), **config)
    parser.cfg["token_vector_width"] = 4
    parser.cfg["hidden_width"] = 32
    # parser.add_label('right')
    parser.add_label("left")
    parser.begin_training([], **parser.cfg)
    sgd = Adam(0.001)

    for i in range(10):
        losses = {}
        doc = Doc(vocab, words=["a", "b", "c", "d"])
        example = Example.from_dict(
            doc, {"heads": [1, 1, 3, 3], "deps": ["left", "ROOT", "left", "ROOT"]}
        )
        parser.update([example], sgd=sgd, losses=losses)
    return parser


def test_no_sentences(parser):
    doc = Doc(parser.vocab, words=["a", "b", "c", "d"])
    doc = parser(doc)
    assert len(list(doc.sents)) >= 1


def test_sents_1(parser):
    doc = Doc(parser.vocab, words=["a", "b", "c", "d"])
    doc[2].sent_start = True
    doc = parser(doc)
    assert len(list(doc.sents)) >= 2
    doc = Doc(parser.vocab, words=["a", "b", "c", "d"])
    doc[1].sent_start = False
    doc[2].sent_start = True
    doc[3].sent_start = False
    doc = parser(doc)
    assert len(list(doc.sents)) == 2


def test_sents_1_2(parser):
    doc = Doc(parser.vocab, words=["a", "b", "c", "d"])
    doc[1].sent_start = True
    doc[2].sent_start = True
    doc = parser(doc)
    assert len(list(doc.sents)) >= 3


def test_sents_1_3(parser):
    doc = Doc(parser.vocab, words=["a", "b", "c", "d"])
    doc[1].sent_start = True
    doc[3].sent_start = True
    doc = parser(doc)
    assert len(list(doc.sents)) >= 3
    doc = Doc(parser.vocab, words=["a", "b", "c", "d"])
    doc[1].sent_start = True
    doc[2].sent_start = False
    doc[3].sent_start = True
    doc = parser(doc)
    assert len(list(doc.sents)) == 3

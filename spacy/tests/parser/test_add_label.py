import pytest
from thinc.api import Adam, fix_random_seed
from spacy.attrs import NORM
from spacy.vocab import Vocab
from spacy.gold import Example
from spacy.pipeline.defaults import default_parser, default_ner
from spacy.tokens import Doc
from spacy.pipeline import DependencyParser, EntityRecognizer


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
    return parser


def test_init_parser(parser):
    pass


def _train_parser(parser):
    fix_random_seed(1)
    parser.add_label("left")
    parser.begin_training([], **parser.cfg)
    sgd = Adam(0.001)

    for i in range(5):
        losses = {}
        doc = Doc(parser.vocab, words=["a", "b", "c", "d"])
        gold = {"heads": [1, 1, 3, 3], "deps": ["left", "ROOT", "left", "ROOT"]}
        example = Example.from_dict(doc, gold)
        parser.update([example], sgd=sgd, losses=losses)
    return parser


def test_add_label(parser):
    parser = _train_parser(parser)
    parser.add_label("right")
    sgd = Adam(0.001)
    for i in range(100):
        losses = {}
        doc = Doc(parser.vocab, words=["a", "b", "c", "d"])
        gold = {"heads": [1, 1, 3, 3], "deps": ["right", "ROOT", "left", "ROOT"]}
        example = Example.from_dict(doc, gold)
        parser.update([example], sgd=sgd, losses=losses)
    doc = Doc(parser.vocab, words=["a", "b", "c", "d"])
    doc = parser(doc)
    assert doc[0].dep_ == "right"
    assert doc[2].dep_ == "left"


def test_add_label_deserializes_correctly():
    config = {
        "learn_tokens": False,
        "min_action_freq": 30,
        "beam_width": 1,
        "beam_update_prob": 1.0,
    }
    ner1 = EntityRecognizer(Vocab(), default_ner(), **config)
    ner1.add_label("C")
    ner1.add_label("B")
    ner1.add_label("A")
    ner1.begin_training([])
    ner2 = EntityRecognizer(Vocab(), default_ner(), **config)

    # the second model needs to be resized before we can call from_bytes
    ner2.model.attrs["resize_output"](ner2.model, ner1.moves.n_moves)
    ner2.from_bytes(ner1.to_bytes())
    assert ner1.moves.n_moves == ner2.moves.n_moves
    for i in range(ner1.moves.n_moves):
        assert ner1.moves.get_class_name(i) == ner2.moves.get_class_name(i)


@pytest.mark.parametrize(
    "pipe_cls,n_moves,model",
    [(DependencyParser, 5, default_parser()), (EntityRecognizer, 4, default_ner())],
)
def test_add_label_get_label(pipe_cls, n_moves, model):
    """Test that added labels are returned correctly. This test was added to
    test for a bug in DependencyParser.labels that'd cause it to fail when
    splitting the move names.
    """
    labels = ["A", "B", "C"]
    pipe = pipe_cls(Vocab(), model)
    for label in labels:
        pipe.add_label(label)
    assert len(pipe.move_names) == len(labels) * n_moves
    pipe_labels = sorted(list(pipe.labels))
    assert pipe_labels == labels

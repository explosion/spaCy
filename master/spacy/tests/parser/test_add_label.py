import pytest
from thinc.api import Adam, fix_random_seed
from spacy import registry
from spacy.language import Language
from spacy.attrs import NORM
from spacy.vocab import Vocab
from spacy.training import Example
from spacy.tokens import Doc
from spacy.pipeline import DependencyParser, EntityRecognizer
from spacy.pipeline.ner import DEFAULT_NER_MODEL
from spacy.pipeline.dep_parser import DEFAULT_PARSER_MODEL


@pytest.fixture
def vocab():
    return Vocab(lex_attr_getters={NORM: lambda s: s})


@pytest.fixture
def parser(vocab):
    cfg = {"model": DEFAULT_PARSER_MODEL}
    model = registry.resolve(cfg, validate=True)["model"]
    parser = DependencyParser(vocab, model)
    return parser


def test_init_parser(parser):
    pass


def _train_parser(parser):
    fix_random_seed(1)
    parser.add_label("left")
    parser.initialize(lambda: [_parser_example(parser)])
    sgd = Adam(0.001)

    for i in range(5):
        losses = {}
        doc = Doc(parser.vocab, words=["a", "b", "c", "d"])
        gold = {"heads": [1, 1, 3, 3], "deps": ["left", "ROOT", "left", "ROOT"]}
        example = Example.from_dict(doc, gold)
        parser.update([example], sgd=sgd, losses=losses)
    return parser


def _parser_example(parser):
    doc = Doc(parser.vocab, words=["a", "b", "c", "d"])
    gold = {"heads": [1, 1, 3, 3], "deps": ["right", "ROOT", "left", "ROOT"]}
    return Example.from_dict(doc, gold)


def _ner_example(ner):
    doc = Doc(
        ner.vocab,
        words=["Joe", "loves", "visiting", "London", "during", "the", "weekend"],
    )
    gold = {"entities": [(0, 3, "PERSON"), (19, 25, "LOC")]}
    return Example.from_dict(doc, gold)


def test_add_label(parser):
    parser = _train_parser(parser)
    parser.add_label("right")
    sgd = Adam(0.001)
    for i in range(100):
        losses = {}
        parser.update([_parser_example(parser)], sgd=sgd, losses=losses)
    doc = Doc(parser.vocab, words=["a", "b", "c", "d"])
    doc = parser(doc)
    assert doc[0].dep_ == "right"
    assert doc[2].dep_ == "left"


def test_add_label_deserializes_correctly():
    cfg = {"model": DEFAULT_NER_MODEL}
    model = registry.resolve(cfg, validate=True)["model"]
    ner1 = EntityRecognizer(Vocab(), model)
    ner1.add_label("C")
    ner1.add_label("B")
    ner1.add_label("A")
    ner1.initialize(lambda: [_ner_example(ner1)])
    ner2 = EntityRecognizer(Vocab(), model)

    # the second model needs to be resized before we can call from_bytes
    ner2.model.attrs["resize_output"](ner2.model, ner1.moves.n_moves)
    ner2.from_bytes(ner1.to_bytes())
    assert ner1.moves.n_moves == ner2.moves.n_moves
    for i in range(ner1.moves.n_moves):
        assert ner1.moves.get_class_name(i) == ner2.moves.get_class_name(i)


@pytest.mark.parametrize(
    "pipe_cls,n_moves,model_config",
    [
        (DependencyParser, 5, DEFAULT_PARSER_MODEL),
        (EntityRecognizer, 4, DEFAULT_NER_MODEL),
    ],
)
def test_add_label_get_label(pipe_cls, n_moves, model_config):
    """Test that added labels are returned correctly. This test was added to
    test for a bug in DependencyParser.labels that'd cause it to fail when
    splitting the move names.
    """
    labels = ["A", "B", "C"]
    model = registry.resolve({"model": model_config}, validate=True)["model"]
    pipe = pipe_cls(Vocab(), model)
    for label in labels:
        pipe.add_label(label)
    assert len(pipe.move_names) == len(labels) * n_moves
    pipe_labels = sorted(list(pipe.labels))
    assert pipe_labels == labels


def test_ner_labels_added_implicitly_on_predict():
    nlp = Language()
    ner = nlp.add_pipe("ner")
    for label in ["A", "B", "C"]:
        ner.add_label(label)
    nlp.initialize()
    doc = Doc(nlp.vocab, words=["hello", "world"], ents=["B-D", "O"])
    ner(doc)
    assert [t.ent_type_ for t in doc] == ["D", ""]
    assert "D" in ner.labels


def test_ner_labels_added_implicitly_on_beam_parse():
    nlp = Language()
    ner = nlp.add_pipe("beam_ner")
    for label in ["A", "B", "C"]:
        ner.add_label(label)
    nlp.initialize()
    doc = Doc(nlp.vocab, words=["hello", "world"], ents=["B-D", "O"])
    ner.beam_parse([doc], beam_width=32)
    assert "D" in ner.labels


def test_ner_labels_added_implicitly_on_greedy_parse():
    nlp = Language()
    ner = nlp.add_pipe("beam_ner")
    for label in ["A", "B", "C"]:
        ner.add_label(label)
    nlp.initialize()
    doc = Doc(nlp.vocab, words=["hello", "world"], ents=["B-D", "O"])
    ner.greedy_parse([doc])
    assert "D" in ner.labels


def test_ner_labels_added_implicitly_on_update():
    nlp = Language()
    ner = nlp.add_pipe("ner")
    for label in ["A", "B", "C"]:
        ner.add_label(label)
    nlp.initialize()
    doc = Doc(nlp.vocab, words=["hello", "world"], ents=["B-D", "O"])
    example = Example(nlp.make_doc(doc.text), doc)
    assert "D" not in ner.labels
    nlp.update([example])
    assert "D" in ner.labels

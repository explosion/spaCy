import pytest
from numpy.testing import assert_equal
from spacy.attrs import ENT_IOB

from spacy import util
from spacy.lang.en import English
from spacy.language import Language
from spacy.lookups import Lookups
from spacy.pipeline._parser_internals.ner import BiluoPushDown
from spacy.training import Example
from spacy.tokens import Doc, Span
from spacy.vocab import Vocab, registry
import logging

from ..util import make_tempdir
from ...pipeline import EntityRecognizer
from ...pipeline.ner import DEFAULT_NER_MODEL

TRAIN_DATA = [
    ("Who is Shaka Khan?", {"entities": [(7, 17, "PERSON")]}),
    ("I like London and Berlin.", {"entities": [(7, 13, "LOC"), (18, 24, "LOC")]}),
]


@pytest.fixture
def neg_key():
    return "non_entities"


@pytest.fixture
def vocab():
    return Vocab()


@pytest.fixture
def doc(vocab):
    return Doc(vocab, words=["Casey", "went", "to", "New", "York", "."])


@pytest.fixture
def entity_annots(doc):
    casey = doc[0:1]
    ny = doc[3:5]
    return [
        (casey.start_char, casey.end_char, "PERSON"),
        (ny.start_char, ny.end_char, "GPE"),
    ]


@pytest.fixture
def entity_types(entity_annots):
    return sorted(set([label for (s, e, label) in entity_annots]))


@pytest.fixture
def tsys(vocab, entity_types):
    actions = BiluoPushDown.get_actions(entity_types=entity_types)
    return BiluoPushDown(vocab.strings, actions)


def test_get_oracle_moves(tsys, doc, entity_annots):
    example = Example.from_dict(doc, {"entities": entity_annots})
    act_classes = tsys.get_oracle_sequence(example, _debug=False)
    names = [tsys.get_class_name(act) for act in act_classes]
    assert names == ["U-PERSON", "O", "O", "B-GPE", "L-GPE", "O"]


def test_negative_samples_two_word_input(tsys, vocab, neg_key):
    """Test that we don't get stuck in a two word input when we have a negative
    span. This could happen if we don't have the right check on the B action.
    """
    tsys.cfg["neg_key"] = neg_key
    doc = Doc(vocab, words=["A", "B"])
    entity_annots = [None, None]
    example = Example.from_dict(doc, {"entities": entity_annots})
    # These mean that the oracle sequence shouldn't have O for the first
    # word, and it shouldn't analyse it as B-PERSON, L-PERSON
    example.y.spans[neg_key] = [
        Span(example.y, 0, 1, label="O"),
        Span(example.y, 0, 2, label="PERSON"),
    ]
    act_classes = tsys.get_oracle_sequence(example)
    names = [tsys.get_class_name(act) for act in act_classes]
    assert names
    assert names[0] != "O"
    assert names[0] != "B-PERSON"
    assert names[1] != "L-PERSON"


def test_negative_samples_three_word_input(tsys, vocab, neg_key):
    """Test that we exclude a 2-word entity correctly using a negative example."""
    tsys.cfg["neg_key"] = neg_key
    doc = Doc(vocab, words=["A", "B", "C"])
    entity_annots = [None, None, None]
    example = Example.from_dict(doc, {"entities": entity_annots})
    # These mean that the oracle sequence shouldn't have O for the first
    # word, and it shouldn't analyse it as B-PERSON, L-PERSON
    example.y.spans[neg_key] = [
        Span(example.y, 0, 1, label="O"),
        Span(example.y, 0, 2, label="PERSON"),
    ]
    act_classes = tsys.get_oracle_sequence(example)
    names = [tsys.get_class_name(act) for act in act_classes]
    assert names
    assert names[0] != "O"
    assert names[1] != "B-PERSON"


def test_negative_samples_U_entity(tsys, vocab, neg_key):
    """Test that we exclude a 2-word entity correctly using a negative example."""
    tsys.cfg["neg_key"] = neg_key
    doc = Doc(vocab, words=["A"])
    entity_annots = [None]
    example = Example.from_dict(doc, {"entities": entity_annots})
    # These mean that the oracle sequence shouldn't have O for the first
    # word, and it shouldn't analyse it as B-PERSON, L-PERSON
    example.y.spans[neg_key] = [
        Span(example.y, 0, 1, label="O"),
        Span(example.y, 0, 1, label="PERSON"),
    ]
    act_classes = tsys.get_oracle_sequence(example)
    names = [tsys.get_class_name(act) for act in act_classes]
    assert names
    assert names[0] != "O"
    assert names[0] != "U-PERSON"


def test_negative_sample_key_is_in_config(vocab, entity_types):
    actions = BiluoPushDown.get_actions(entity_types=entity_types)
    tsys = BiluoPushDown(vocab.strings, actions, incorrect_spans_key="non_entities")
    assert tsys.cfg["neg_key"] == "non_entities"


# We can't easily represent this on a Doc object. Not sure what the best solution
# would be, but I don't think it's an important use case?
@pytest.mark.skip(reason="No longer supported")
def test_oracle_moves_missing_B(en_vocab):
    words = ["B", "52", "Bomber"]
    biluo_tags = [None, None, "L-PRODUCT"]

    doc = Doc(en_vocab, words=words)
    example = Example.from_dict(doc, {"words": words, "entities": biluo_tags})

    moves = BiluoPushDown(en_vocab.strings)
    move_types = ("M", "B", "I", "L", "U", "O")
    for tag in biluo_tags:
        if tag is None:
            continue
        elif tag == "O":
            moves.add_action(move_types.index("O"), "")
        else:
            action, label = tag.split("-")
            moves.add_action(move_types.index("B"), label)
            moves.add_action(move_types.index("I"), label)
            moves.add_action(move_types.index("L"), label)
            moves.add_action(move_types.index("U"), label)
    moves.get_oracle_sequence(example)


# We can't easily represent this on a Doc object. Not sure what the best solution
# would be, but I don't think it's an important use case?
@pytest.mark.skip(reason="No longer supported")
def test_oracle_moves_whitespace(en_vocab):
    words = ["production", "\n", "of", "Northrop", "\n", "Corp.", "\n", "'s", "radar"]
    biluo_tags = ["O", "O", "O", "B-ORG", None, "I-ORG", "L-ORG", "O", "O"]

    doc = Doc(en_vocab, words=words)
    example = Example.from_dict(doc, {"entities": biluo_tags})

    moves = BiluoPushDown(en_vocab.strings)
    move_types = ("M", "B", "I", "L", "U", "O")
    for tag in biluo_tags:
        if tag is None:
            continue
        elif tag == "O":
            moves.add_action(move_types.index("O"), "")
        else:
            action, label = tag.split("-")
            moves.add_action(move_types.index(action), label)
    moves.get_oracle_sequence(example)


def test_accept_blocked_token():
    """Test succesful blocking of tokens to be in an entity."""
    # 1. test normal behaviour
    nlp1 = English()
    doc1 = nlp1("I live in New York")
    config = {}
    ner1 = nlp1.create_pipe("ner", config=config)
    assert [token.ent_iob_ for token in doc1] == ["", "", "", "", ""]
    assert [token.ent_type_ for token in doc1] == ["", "", "", "", ""]

    # Add the OUT action
    ner1.moves.add_action(5, "")
    ner1.add_label("GPE")
    # Get into the state just before "New"
    state1 = ner1.moves.init_batch([doc1])[0]
    ner1.moves.apply_transition(state1, "O")
    ner1.moves.apply_transition(state1, "O")
    ner1.moves.apply_transition(state1, "O")
    # Check that B-GPE is valid.
    assert ner1.moves.is_valid(state1, "B-GPE")

    # 2. test blocking behaviour
    nlp2 = English()
    doc2 = nlp2("I live in New York")
    config = {}
    ner2 = nlp2.create_pipe("ner", config=config)

    # set "New York" to a blocked entity
    doc2.set_ents([], blocked=[doc2[3:5]], default="unmodified")
    assert [token.ent_iob_ for token in doc2] == ["", "", "", "B", "B"]
    assert [token.ent_type_ for token in doc2] == ["", "", "", "", ""]

    # Check that B-GPE is now invalid.
    ner2.moves.add_action(4, "")
    ner2.moves.add_action(5, "")
    ner2.add_label("GPE")
    state2 = ner2.moves.init_batch([doc2])[0]
    ner2.moves.apply_transition(state2, "O")
    ner2.moves.apply_transition(state2, "O")
    ner2.moves.apply_transition(state2, "O")
    # we can only use U- for "New"
    assert not ner2.moves.is_valid(state2, "B-GPE")
    assert ner2.moves.is_valid(state2, "U-")
    ner2.moves.apply_transition(state2, "U-")
    # we can only use U- for "York"
    assert not ner2.moves.is_valid(state2, "B-GPE")
    assert ner2.moves.is_valid(state2, "U-")


def test_train_empty():
    """Test that training an empty text does not throw errors."""
    train_data = [
        ("Who is Shaka Khan?", {"entities": [(7, 17, "PERSON")]}),
        ("", {"entities": []}),
    ]

    nlp = English()
    train_examples = []
    for t in train_data:
        train_examples.append(Example.from_dict(nlp.make_doc(t[0]), t[1]))
    ner = nlp.add_pipe("ner", last=True)
    ner.add_label("PERSON")
    nlp.initialize()
    for itn in range(2):
        losses = {}
        batches = util.minibatch(train_examples, size=8)
        for batch in batches:
            nlp.update(batch, losses=losses)


def test_train_negative_deprecated():
    """Test that the deprecated negative entity format raises a custom error."""
    train_data = [
        ("Who is Shaka Khan?", {"entities": [(7, 17, "!PERSON")]}),
    ]

    nlp = English()
    train_examples = []
    for t in train_data:
        train_examples.append(Example.from_dict(nlp.make_doc(t[0]), t[1]))
    ner = nlp.add_pipe("ner", last=True)
    ner.add_label("PERSON")
    nlp.initialize()
    for itn in range(2):
        losses = {}
        batches = util.minibatch(train_examples, size=8)
        for batch in batches:
            with pytest.raises(ValueError):
                nlp.update(batch, losses=losses)


def test_overwrite_token():
    nlp = English()
    nlp.add_pipe("ner")
    nlp.initialize()
    # The untrained NER will predict O for each token
    doc = nlp("I live in New York")
    assert [token.ent_iob_ for token in doc] == ["O", "O", "O", "O", "O"]
    assert [token.ent_type_ for token in doc] == ["", "", "", "", ""]
    # Check that a new ner can overwrite O
    config = {}
    ner2 = nlp.create_pipe("ner", config=config)
    ner2.moves.add_action(5, "")
    ner2.add_label("GPE")
    state = ner2.moves.init_batch([doc])[0]
    assert ner2.moves.is_valid(state, "B-GPE")
    assert ner2.moves.is_valid(state, "U-GPE")
    ner2.moves.apply_transition(state, "B-GPE")
    assert ner2.moves.is_valid(state, "I-GPE")
    assert ner2.moves.is_valid(state, "L-GPE")


def test_empty_ner():
    nlp = English()
    ner = nlp.add_pipe("ner")
    ner.add_label("MY_LABEL")
    nlp.initialize()
    doc = nlp("John is watching the news about Croatia's elections")
    # if this goes wrong, the initialization of the parser's upper layer is probably broken
    result = ["O", "O", "O", "O", "O", "O", "O", "O", "O"]
    assert [token.ent_iob_ for token in doc] == result


def test_ruler_before_ner():
    """Test that an NER works after an entity_ruler: the second can add annotations"""
    nlp = English()

    # 1 : Entity Ruler - should set "this" to B and everything else to empty
    patterns = [{"label": "THING", "pattern": "This"}]
    ruler = nlp.add_pipe("entity_ruler")

    # 2: untrained NER - should set everything else to O
    untrained_ner = nlp.add_pipe("ner")
    untrained_ner.add_label("MY_LABEL")
    nlp.initialize()
    ruler.add_patterns(patterns)
    doc = nlp("This is Antti Korhonen speaking in Finland")
    expected_iobs = ["B", "O", "O", "O", "O", "O", "O"]
    expected_types = ["THING", "", "", "", "", "", ""]
    assert [token.ent_iob_ for token in doc] == expected_iobs
    assert [token.ent_type_ for token in doc] == expected_types


def test_ner_constructor(en_vocab):
    config = {
        "update_with_oracle_cut_size": 100,
    }
    cfg = {"model": DEFAULT_NER_MODEL}
    model = registry.resolve(cfg, validate=True)["model"]
    EntityRecognizer(en_vocab, model, **config)
    EntityRecognizer(en_vocab, model)


def test_ner_before_ruler():
    """Test that an entity_ruler works after an NER: the second can overwrite O annotations"""
    nlp = English()

    # 1: untrained NER - should set everything to O
    untrained_ner = nlp.add_pipe("ner", name="uner")
    untrained_ner.add_label("MY_LABEL")
    nlp.initialize()

    # 2 : Entity Ruler - should set "this" to B and keep everything else O
    patterns = [{"label": "THING", "pattern": "This"}]
    ruler = nlp.add_pipe("entity_ruler")
    ruler.add_patterns(patterns)

    doc = nlp("This is Antti Korhonen speaking in Finland")
    expected_iobs = ["B", "O", "O", "O", "O", "O", "O"]
    expected_types = ["THING", "", "", "", "", "", ""]
    assert [token.ent_iob_ for token in doc] == expected_iobs
    assert [token.ent_type_ for token in doc] == expected_types


def test_block_ner():
    """Test functionality for blocking tokens so they can't be in a named entity"""
    # block "Antti L Korhonen" from being a named entity
    nlp = English()
    nlp.add_pipe("blocker", config={"start": 2, "end": 5})
    untrained_ner = nlp.add_pipe("ner")
    untrained_ner.add_label("MY_LABEL")
    nlp.initialize()
    doc = nlp("This is Antti L Korhonen speaking in Finland")
    expected_iobs = ["O", "O", "B", "B", "B", "O", "O", "O"]
    expected_types = ["", "", "", "", "", "", "", ""]
    assert [token.ent_iob_ for token in doc] == expected_iobs
    assert [token.ent_type_ for token in doc] == expected_types


@pytest.mark.parametrize("use_upper", [True, False])
def test_overfitting_IO(use_upper):
    # Simple test to try and quickly overfit the NER component
    nlp = English()
    ner = nlp.add_pipe("ner", config={"model": {"use_upper": use_upper}})
    train_examples = []
    for text, annotations in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(text), annotations))
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])
    optimizer = nlp.initialize()

    for i in range(50):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
    assert losses["ner"] < 0.00001

    # test the trained model
    test_text = "I like London."
    doc = nlp(test_text)
    ents = doc.ents
    assert len(ents) == 1
    assert ents[0].text == "London"
    assert ents[0].label_ == "LOC"

    # Also test the results are still the same after IO
    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = util.load_model_from_path(tmp_dir)
        doc2 = nlp2(test_text)
        ents2 = doc2.ents
        assert len(ents2) == 1
        assert ents2[0].text == "London"
        assert ents2[0].label_ == "LOC"
        # Ensure that the predictions are still the same, even after adding a new label
        ner2 = nlp2.get_pipe("ner")
        assert ner2.model.attrs["has_upper"] == use_upper
        ner2.add_label("RANDOM_NEW_LABEL")
        doc3 = nlp2(test_text)
        ents3 = doc3.ents
        assert len(ents3) == 1
        assert ents3[0].text == "London"
        assert ents3[0].label_ == "LOC"

    # Make sure that running pipe twice, or comparing to call, always amounts to the same predictions
    texts = [
        "Just a sentence.",
        "Then one more sentence about London.",
        "Here is another one.",
        "I like London.",
    ]
    batch_deps_1 = [doc.to_array([ENT_IOB]) for doc in nlp.pipe(texts)]
    batch_deps_2 = [doc.to_array([ENT_IOB]) for doc in nlp.pipe(texts)]
    no_batch_deps = [doc.to_array([ENT_IOB]) for doc in [nlp(text) for text in texts]]
    assert_equal(batch_deps_1, batch_deps_2)
    assert_equal(batch_deps_1, no_batch_deps)

    # test that kb_id is preserved
    test_text = "I like London and London."
    doc = nlp.make_doc(test_text)
    doc.ents = [Span(doc, 2, 3, label="LOC", kb_id=1234)]
    ents = doc.ents
    assert len(ents) == 1
    assert ents[0].text == "London"
    assert ents[0].label_ == "LOC"
    assert ents[0].kb_id == 1234
    doc = nlp.get_pipe("ner")(doc)
    ents = doc.ents
    assert len(ents) == 2
    assert ents[0].text == "London"
    assert ents[0].label_ == "LOC"
    assert ents[0].kb_id == 1234
    # ent added by ner has kb_id == 0
    assert ents[1].text == "London"
    assert ents[1].label_ == "LOC"
    assert ents[1].kb_id == 0


def test_beam_ner_scores():
    # Test that we can get confidence values out of the beam_ner pipe
    beam_width = 16
    beam_density = 0.0001
    nlp = English()
    config = {
        "beam_width": beam_width,
        "beam_density": beam_density,
    }
    ner = nlp.add_pipe("beam_ner", config=config)
    train_examples = []
    for text, annotations in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(text), annotations))
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])
    optimizer = nlp.initialize()

    # update once
    losses = {}
    nlp.update(train_examples, sgd=optimizer, losses=losses)

    # test the scores from the beam
    test_text = "I like London."
    doc = nlp.make_doc(test_text)
    docs = [doc]
    beams = ner.predict(docs)
    entity_scores = ner.scored_ents(beams)[0]

    for j in range(len(doc)):
        for label in ner.labels:
            score = entity_scores[(j, j + 1, label)]
            eps = 0.00001
            assert 0 - eps <= score <= 1 + eps


def test_beam_overfitting_IO(neg_key):
    # Simple test to try and quickly overfit the Beam NER component
    nlp = English()
    beam_width = 16
    beam_density = 0.0001
    config = {
        "beam_width": beam_width,
        "beam_density": beam_density,
        "incorrect_spans_key": neg_key,
    }
    ner = nlp.add_pipe("beam_ner", config=config)
    train_examples = []
    for text, annotations in TRAIN_DATA:
        train_examples.append(Example.from_dict(nlp.make_doc(text), annotations))
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])
    optimizer = nlp.initialize()

    # run overfitting
    for i in range(50):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)
    assert losses["beam_ner"] < 0.0001

    # test the scores from the beam
    test_text = "I like London"
    docs = [nlp.make_doc(test_text)]
    beams = ner.predict(docs)
    entity_scores = ner.scored_ents(beams)[0]
    assert entity_scores[(2, 3, "LOC")] == 1.0
    assert entity_scores[(2, 3, "PERSON")] == 0.0
    assert len(nlp(test_text).ents) == 1

    # Also test the results are still the same after IO
    with make_tempdir() as tmp_dir:
        nlp.to_disk(tmp_dir)
        nlp2 = util.load_model_from_path(tmp_dir)
        docs2 = [nlp2.make_doc(test_text)]
        ner2 = nlp2.get_pipe("beam_ner")
        beams2 = ner2.predict(docs2)
        entity_scores2 = ner2.scored_ents(beams2)[0]
        assert entity_scores2[(2, 3, "LOC")] == 1.0
        assert entity_scores2[(2, 3, "PERSON")] == 0.0

    # Try to unlearn the entity by using negative annotations
    neg_doc = nlp.make_doc(test_text)
    neg_ex = Example(neg_doc, neg_doc)
    neg_ex.reference.spans[neg_key] = [Span(neg_doc, 2, 3, "LOC")]
    neg_train_examples = [neg_ex]

    for i in range(20):
        losses = {}
        nlp.update(neg_train_examples, sgd=optimizer, losses=losses)

    # test the "untrained" model
    assert len(nlp(test_text).ents) == 0


def test_neg_annotation(neg_key):
    """Check that the NER update works with a negative annotation that is a different label of the correct one,
    or partly overlapping, etc"""
    nlp = English()
    beam_width = 16
    beam_density = 0.0001
    config = {
        "beam_width": beam_width,
        "beam_density": beam_density,
        "incorrect_spans_key": neg_key,
    }
    ner = nlp.add_pipe("beam_ner", config=config)
    train_text = "Who is Shaka Khan?"
    neg_doc = nlp.make_doc(train_text)
    ner.add_label("PERSON")
    ner.add_label("ORG")
    example = Example.from_dict(neg_doc, {"entities": [(7, 17, "PERSON")]})
    example.reference.spans[neg_key] = [
        Span(neg_doc, 2, 4, "ORG"),
        Span(neg_doc, 2, 3, "PERSON"),
        Span(neg_doc, 1, 4, "PERSON"),
    ]

    optimizer = nlp.initialize()
    for i in range(2):
        losses = {}
        nlp.update([example], sgd=optimizer, losses=losses)


def test_neg_annotation_conflict(neg_key):
    # Check that NER raises for a negative annotation that is THE SAME as a correct one
    nlp = English()
    beam_width = 16
    beam_density = 0.0001
    config = {
        "beam_width": beam_width,
        "beam_density": beam_density,
        "incorrect_spans_key": neg_key,
    }
    ner = nlp.add_pipe("beam_ner", config=config)
    train_text = "Who is Shaka Khan?"
    neg_doc = nlp.make_doc(train_text)
    ner.add_label("PERSON")
    ner.add_label("LOC")
    example = Example.from_dict(neg_doc, {"entities": [(7, 17, "PERSON")]})
    example.reference.spans[neg_key] = [Span(neg_doc, 2, 4, "PERSON")]
    assert len(example.reference.ents) == 1
    assert example.reference.ents[0].text == "Shaka Khan"
    assert example.reference.ents[0].label_ == "PERSON"
    assert len(example.reference.spans[neg_key]) == 1
    assert example.reference.spans[neg_key][0].text == "Shaka Khan"
    assert example.reference.spans[neg_key][0].label_ == "PERSON"

    optimizer = nlp.initialize()
    for i in range(2):
        losses = {}
        with pytest.raises(ValueError):
            nlp.update([example], sgd=optimizer, losses=losses)


def test_beam_valid_parse(neg_key):
    """Regression test for previously flakey behaviour"""
    nlp = English()
    beam_width = 16
    beam_density = 0.0001
    config = {
        "beam_width": beam_width,
        "beam_density": beam_density,
        "incorrect_spans_key": neg_key,
    }
    nlp.add_pipe("beam_ner", config=config)
    # fmt: off
    tokens = ['FEDERAL', 'NATIONAL', 'MORTGAGE', 'ASSOCIATION', '(', 'Fannie', 'Mae', '):', 'Posted', 'yields', 'on', '30', 'year', 'mortgage', 'commitments', 'for', 'delivery', 'within', '30', 'days', '(', 'priced', 'at', 'par', ')', '9.75', '%', ',', 'standard', 'conventional', 'fixed', '-', 'rate', 'mortgages', ';', '8.70', '%', ',', '6/2', 'rate', 'capped', 'one', '-', 'year', 'adjustable', 'rate', 'mortgages', '.', 'Source', ':', 'Telerate', 'Systems', 'Inc.']
    iob = ['B-ORG', 'I-ORG', 'I-ORG', 'L-ORG', 'O', 'B-ORG', 'L-ORG', 'O', 'O', 'O', 'O', 'B-DATE', 'L-DATE', 'O', 'O', 'O', 'O', 'O', 'B-DATE', 'L-DATE', 'O', 'O', 'O', 'O', 'O', 'B-PERCENT', 'L-PERCENT', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'B-PERCENT', 'L-PERCENT', 'O', 'U-CARDINAL', 'O', 'O', 'B-DATE', 'I-DATE', 'L-DATE', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']
    # fmt: on

    doc = Doc(nlp.vocab, words=tokens)
    example = Example.from_dict(doc, {"ner": iob})
    neg_span = Span(doc, 50, 53, "ORG")
    example.reference.spans[neg_key] = [neg_span]

    optimizer = nlp.initialize()

    for i in range(5):
        losses = {}
        nlp.update([example], sgd=optimizer, losses=losses)
    assert "beam_ner" in losses


def test_ner_warns_no_lookups(caplog):
    nlp = English()
    assert nlp.lang in util.LEXEME_NORM_LANGS
    nlp.vocab.lookups = Lookups()
    assert not len(nlp.vocab.lookups)
    nlp.add_pipe("ner")
    with caplog.at_level(logging.DEBUG):
        nlp.initialize()
        assert "W033" in caplog.text
    caplog.clear()
    nlp.vocab.lookups.add_table("lexeme_norm")
    nlp.vocab.lookups.get_table("lexeme_norm")["a"] = "A"
    with caplog.at_level(logging.DEBUG):
        nlp.initialize()
        assert "W033" not in caplog.text


@Language.factory("blocker")
class BlockerComponent1:
    def __init__(self, nlp, start, end, name="my_blocker"):
        self.start = start
        self.end = end
        self.name = name

    def __call__(self, doc):
        doc.set_ents([], blocked=[doc[self.start : self.end]], default="unmodified")
        return doc

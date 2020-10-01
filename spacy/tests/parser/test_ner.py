import pytest
from spacy import util
from spacy.lang.en import English
from spacy.language import Language
from spacy.lookups import Lookups
from spacy.pipeline._parser_internals.ner import BiluoPushDown
from spacy.training import Example
from spacy.tokens import Doc
from spacy.vocab import Vocab
import logging

from ..util import make_tempdir


TRAIN_DATA = [
    ("Who is Shaka Khan?", {"entities": [(7, 17, "PERSON")]}),
    ("I like London and Berlin.", {"entities": [(7, 13, "LOC"), (18, 24, "LOC")]}),
]


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
    act_classes = tsys.get_oracle_sequence(example)
    names = [tsys.get_class_name(act) for act in act_classes]
    assert names == ["U-PERSON", "O", "O", "B-GPE", "L-GPE", "O"]


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_get_oracle_moves_negative_entities(tsys, doc, entity_annots):
    entity_annots = [(s, e, "!" + label) for s, e, label in entity_annots]
    example = Example.from_dict(doc, {"entities": entity_annots})
    ex_dict = example.to_dict()

    for i, tag in enumerate(ex_dict["doc_annotation"]["entities"]):
        if tag == "L-!GPE":
            ex_dict["doc_annotation"]["entities"][i] = "-"
    example = Example.from_dict(doc, ex_dict)

    act_classes = tsys.get_oracle_sequence(example)
    names = [tsys.get_class_name(act) for act in act_classes]
    assert names


def test_get_oracle_moves_negative_entities2(tsys, vocab):
    doc = Doc(vocab, words=["A", "B", "C", "D"])
    entity_annots = ["B-!PERSON", "L-!PERSON", "B-!PERSON", "L-!PERSON"]
    example = Example.from_dict(doc, {"entities": entity_annots})
    act_classes = tsys.get_oracle_sequence(example)
    names = [tsys.get_class_name(act) for act in act_classes]
    assert names


@pytest.mark.skip(reason="Maybe outdated? Unsure")
def test_get_oracle_moves_negative_O(tsys, vocab):
    doc = Doc(vocab, words=["A", "B", "C", "D"])
    entity_annots = ["O", "!O", "O", "!O"]
    example = Example.from_dict(doc, {"entities": entity_annots})
    act_classes = tsys.get_oracle_sequence(example)
    names = [tsys.get_class_name(act) for act in act_classes]
    assert names


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
    """ Test that an NER works after an entity_ruler: the second can add annotations """
    nlp = English()

    # 1 : Entity Ruler - should set "this" to B and everything else to empty
    patterns = [{"label": "THING", "pattern": "This"}]
    ruler = nlp.add_pipe("entity_ruler")
    ruler.add_patterns(patterns)

    # 2: untrained NER - should set everything else to O
    untrained_ner = nlp.add_pipe("ner")
    untrained_ner.add_label("MY_LABEL")
    nlp.initialize()
    doc = nlp("This is Antti Korhonen speaking in Finland")
    expected_iobs = ["B", "O", "O", "O", "O", "O", "O"]
    expected_types = ["THING", "", "", "", "", "", ""]
    assert [token.ent_iob_ for token in doc] == expected_iobs
    assert [token.ent_type_ for token in doc] == expected_types


def test_ner_before_ruler():
    """ Test that an entity_ruler works after an NER: the second can overwrite O annotations """
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
    """ Test functionality for blocking tokens so they can't be in a named entity """
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


def test_overfitting_IO():
    # Simple test to try and quickly overfit the NER component - ensuring the ML models work correctly
    nlp = English()
    ner = nlp.add_pipe("ner")
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

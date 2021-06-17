import pytest
from spacy import registry
from spacy.lang.en import English
from spacy.lang.de import German
from spacy.pipeline.ner import DEFAULT_NER_MODEL
from spacy.pipeline import EntityRuler, EntityRecognizer
from spacy.matcher import Matcher, PhraseMatcher
from spacy.tokens import Doc
from spacy.vocab import Vocab
from spacy.attrs import ENT_IOB, ENT_TYPE
from spacy.compat import pickle
from spacy import displacy
from spacy.vectors import Vectors
import numpy


def test_issue3002():
    """Test that the tokenizer doesn't hang on a long list of dots"""
    nlp = German()
    doc = nlp(
        "880.794.982.218.444.893.023.439.794.626.120.190.780.624.990.275.671 ist eine lange Zahl"
    )
    assert len(doc) == 5


def test_issue3009(en_vocab):
    """Test problem with matcher quantifiers"""
    patterns = [
        [{"ORTH": "has"}, {"LOWER": "to"}, {"LOWER": "do"}, {"TAG": "IN"}],
        [
            {"ORTH": "has"},
            {"IS_ASCII": True, "IS_PUNCT": False, "OP": "*"},
            {"LOWER": "to"},
            {"LOWER": "do"},
            {"TAG": "IN"},
        ],
        [
            {"ORTH": "has"},
            {"IS_ASCII": True, "IS_PUNCT": False, "OP": "?"},
            {"LOWER": "to"},
            {"LOWER": "do"},
            {"TAG": "IN"},
        ],
    ]
    words = ["also", "has", "to", "do", "with"]
    tags = ["RB", "VBZ", "TO", "VB", "IN"]
    pos = ["ADV", "VERB", "ADP", "VERB", "ADP"]
    doc = Doc(en_vocab, words=words, tags=tags, pos=pos)
    matcher = Matcher(en_vocab)
    for i, pattern in enumerate(patterns):
        matcher.add(str(i), [pattern])
        matches = matcher(doc)
        assert matches


def test_issue3012(en_vocab):
    """Test that the is_tagged attribute doesn't get overwritten when we from_array
    without tag information."""
    words = ["This", "is", "10", "%", "."]
    tags = ["DT", "VBZ", "CD", "NN", "."]
    pos = ["DET", "VERB", "NUM", "NOUN", "PUNCT"]
    ents = ["O", "O", "B-PERCENT", "I-PERCENT", "O"]
    doc = Doc(en_vocab, words=words, tags=tags, pos=pos, ents=ents)
    assert doc.has_annotation("TAG")
    expected = ("10", "NUM", "CD", "PERCENT")
    assert (doc[2].text, doc[2].pos_, doc[2].tag_, doc[2].ent_type_) == expected
    header = [ENT_IOB, ENT_TYPE]
    ent_array = doc.to_array(header)
    doc.from_array(header, ent_array)
    assert (doc[2].text, doc[2].pos_, doc[2].tag_, doc[2].ent_type_) == expected
    # Serializing then deserializing
    doc_bytes = doc.to_bytes()
    doc2 = Doc(en_vocab).from_bytes(doc_bytes)
    assert (doc2[2].text, doc2[2].pos_, doc2[2].tag_, doc2[2].ent_type_) == expected


def test_issue3199():
    """Test that Span.noun_chunks works correctly if no noun chunks iterator
    is available. To make this test future-proof, we're constructing a Doc
    with a new Vocab here and a parse tree to make sure the noun chunks run.
    """
    words = ["This", "is", "a", "sentence"]
    doc = Doc(Vocab(), words=words, heads=[0] * len(words), deps=["dep"] * len(words))
    with pytest.raises(NotImplementedError):
        list(doc[0:3].noun_chunks)


def test_issue3209():
    """Test issue that occurred in spaCy nightly where NER labels were being
    mapped to classes incorrectly after loading the model, when the labels
    were added using ner.add_label().
    """
    nlp = English()
    ner = nlp.add_pipe("ner")
    ner.add_label("ANIMAL")
    nlp.initialize()
    move_names = ["O", "B-ANIMAL", "I-ANIMAL", "L-ANIMAL", "U-ANIMAL"]
    assert ner.move_names == move_names
    nlp2 = English()
    ner2 = nlp2.add_pipe("ner")
    model = ner2.model
    model.attrs["resize_output"](model, ner.moves.n_moves)
    nlp2.from_bytes(nlp.to_bytes())
    assert ner2.move_names == move_names


def test_issue3248_1():
    """Test that the PhraseMatcher correctly reports its number of rules, not
    total number of patterns."""
    nlp = English()
    matcher = PhraseMatcher(nlp.vocab)
    matcher.add("TEST1", [nlp("a"), nlp("b"), nlp("c")])
    matcher.add("TEST2", [nlp("d")])
    assert len(matcher) == 2


def test_issue3248_2():
    """Test that the PhraseMatcher can be pickled correctly."""
    nlp = English()
    matcher = PhraseMatcher(nlp.vocab)
    matcher.add("TEST1", [nlp("a"), nlp("b"), nlp("c")])
    matcher.add("TEST2", [nlp("d")])
    data = pickle.dumps(matcher)
    new_matcher = pickle.loads(data)
    assert len(new_matcher) == len(matcher)


def test_issue3277(es_tokenizer):
    """Test that hyphens are split correctly as prefixes."""
    doc = es_tokenizer("—Yo me llamo... –murmuró el niño– Emilio Sánchez Pérez.")
    assert len(doc) == 14
    assert doc[0].text == "\u2014"
    assert doc[5].text == "\u2013"
    assert doc[9].text == "\u2013"


def test_issue3288(en_vocab):
    """Test that retokenization works correctly via displaCy when punctuation
    is merged onto the preceeding token and tensor is resized."""
    words = ["Hello", "World", "!", "When", "is", "this", "breaking", "?"]
    heads = [1, 1, 1, 4, 4, 6, 4, 4]
    deps = ["intj", "ROOT", "punct", "advmod", "ROOT", "det", "nsubj", "punct"]
    doc = Doc(en_vocab, words=words, heads=heads, deps=deps)
    doc.tensor = numpy.zeros((len(words), 96), dtype="float32")
    displacy.render(doc)


def test_issue3289():
    """Test that Language.to_bytes handles serializing a pipeline component
    with an uninitialized model."""
    nlp = English()
    nlp.add_pipe("textcat")
    bytes_data = nlp.to_bytes()
    new_nlp = English()
    new_nlp.add_pipe("textcat")
    new_nlp.from_bytes(bytes_data)


def test_issue3328(en_vocab):
    doc = Doc(en_vocab, words=["Hello", ",", "how", "are", "you", "doing", "?"])
    matcher = Matcher(en_vocab)
    patterns = [
        [{"LOWER": {"IN": ["hello", "how"]}}],
        [{"LOWER": {"IN": ["you", "doing"]}}],
    ]
    matcher.add("TEST", patterns)
    matches = matcher(doc)
    assert len(matches) == 4
    matched_texts = [doc[start:end].text for _, start, end in matches]
    assert matched_texts == ["Hello", "how", "you", "doing"]


def test_issue3331(en_vocab):
    """Test that duplicate patterns for different rules result in multiple
    matches, one per rule.
    """
    matcher = PhraseMatcher(en_vocab)
    matcher.add("A", [Doc(en_vocab, words=["Barack", "Obama"])])
    matcher.add("B", [Doc(en_vocab, words=["Barack", "Obama"])])
    doc = Doc(en_vocab, words=["Barack", "Obama", "lifts", "America"])
    matches = matcher(doc)
    assert len(matches) == 2
    match_ids = [en_vocab.strings[matches[0][0]], en_vocab.strings[matches[1][0]]]
    assert sorted(match_ids) == ["A", "B"]


def test_issue3345():
    """Test case where preset entity crosses sentence boundary."""
    nlp = English()
    doc = Doc(nlp.vocab, words=["I", "live", "in", "New", "York"])
    doc[4].is_sent_start = True
    ruler = EntityRuler(nlp, patterns=[{"label": "GPE", "pattern": "New York"}])
    cfg = {"model": DEFAULT_NER_MODEL}
    model = registry.resolve(cfg, validate=True)["model"]
    ner = EntityRecognizer(doc.vocab, model)
    # Add the OUT action. I wouldn't have thought this would be necessary...
    ner.moves.add_action(5, "")
    ner.add_label("GPE")
    doc = ruler(doc)
    # Get into the state just before "New"
    state = ner.moves.init_batch([doc])[0]
    ner.moves.apply_transition(state, "O")
    ner.moves.apply_transition(state, "O")
    ner.moves.apply_transition(state, "O")
    # Check that B-GPE is valid.
    assert ner.moves.is_valid(state, "B-GPE")


def test_issue3412():
    data = numpy.asarray([[0, 0, 0], [1, 2, 3], [9, 8, 7]], dtype="f")
    vectors = Vectors(data=data, keys=["A", "B", "C"])
    keys, best_rows, scores = vectors.most_similar(
        numpy.asarray([[9, 8, 7], [0, 0, 0]], dtype="f")
    )
    assert best_rows[0] == 2


@pytest.mark.skip(reason="default suffix rules avoid one upper-case letter before dot")
def test_issue3449():
    nlp = English()
    nlp.add_pipe("sentencizer")
    text1 = "He gave the ball to I. Do you want to go to the movies with I?"
    text2 = "He gave the ball to I.  Do you want to go to the movies with I?"
    text3 = "He gave the ball to I.\nDo you want to go to the movies with I?"
    t1 = nlp(text1)
    t2 = nlp(text2)
    t3 = nlp(text3)
    assert t1[5].text == "I"
    assert t2[5].text == "I"
    assert t3[5].text == "I"


def test_issue3456():
    # this crashed because of a padding error in layer.ops.unflatten in thinc
    nlp = English()
    tagger = nlp.add_pipe("tagger")
    tagger.add_label("A")
    nlp.initialize()
    list(nlp.pipe(["hi", ""]))


def test_issue3468():
    """Test that sentence boundaries are set correctly so Doc.has_annotation("SENT_START") can
    be restored after serialization."""
    nlp = English()
    nlp.add_pipe("sentencizer")
    doc = nlp("Hello world")
    assert doc[0].is_sent_start
    assert doc.has_annotation("SENT_START")
    assert len(list(doc.sents)) == 1
    doc_bytes = doc.to_bytes()
    new_doc = Doc(nlp.vocab).from_bytes(doc_bytes)
    assert new_doc[0].is_sent_start
    assert new_doc.has_annotation("SENT_START")
    assert len(list(new_doc.sents)) == 1

# coding: utf8
from __future__ import unicode_literals

import pytest
import gc
import numpy
import copy
from spacy.lang.en import English
from spacy.lang.en.stop_words import STOP_WORDS
from spacy.lang.lex_attrs import is_stop
from spacy.vectors import Vectors
from spacy.vocab import Vocab
from spacy.language import Language
from spacy.tokens import Doc, Span, Token
from spacy.pipeline import Tagger, EntityRecognizer
from spacy.attrs import HEAD, DEP
from spacy.matcher import Matcher

from ..util import make_tempdir


def test_issue1506():
    def string_generator():
        for _ in range(10001):
            yield "It's sentence produced by that bug."
        for _ in range(10001):
            yield "I erase some hbdsaj lemmas."
        for _ in range(10001):
            yield "I erase lemmas."
        for _ in range(10001):
            yield "It's sentence produced by that bug."
        for _ in range(10001):
            yield "It's sentence produced by that bug."

    nlp = English()
    for i, d in enumerate(nlp.pipe(string_generator())):
        # We should run cleanup more than one time to actually cleanup data.
        # In first run — clean up only mark strings as «not hitted».
        if i == 10000 or i == 20000 or i == 30000:
            gc.collect()
        for t in d:
            str(t.lemma_)


def test_issue1518():
    """Test vectors.resize() works."""
    vectors = Vectors(shape=(10, 10))
    vectors.add("hello", row=2)
    vectors.resize((5, 9))


def test_issue1537():
    """Test that Span.as_doc() doesn't segfault."""
    string = "The sky is blue . The man is pink . The dog is purple ."
    doc = Doc(Vocab(), words=string.split())
    doc[0].sent_start = True
    for word in doc[1:]:
        if word.nbor(-1).text == ".":
            word.sent_start = True
        else:
            word.sent_start = False
    sents = list(doc.sents)
    sent0 = sents[0].as_doc()
    sent1 = sents[1].as_doc()
    assert isinstance(sent0, Doc)
    assert isinstance(sent1, Doc)


# TODO: Currently segfaulting, due to l_edge and r_edge misalignment
# def test_issue1537_model():
#    nlp = load_spacy('en')
#    doc = nlp('The sky is blue. The man is pink. The dog is purple.')
#    sents = [s.as_doc() for s in doc.sents]
#    print(list(sents[0].noun_chunks))
#    print(list(sents[1].noun_chunks))


def test_issue1539():
    """Ensure vectors.resize() doesn't try to modify dictionary during iteration."""
    v = Vectors(shape=(10, 10), keys=[5, 3, 98, 100])
    v.resize((100, 100))


def test_issue1547():
    """Test that entity labels still match after merging tokens."""
    words = ["\n", "worda", ".", "\n", "wordb", "-", "Biosphere", "2", "-", " \n"]
    doc = Doc(Vocab(), words=words)
    doc.ents = [Span(doc, 6, 8, label=doc.vocab.strings["PRODUCT"])]
    with doc.retokenize() as retokenizer:
        retokenizer.merge(doc[5:7])
    assert [ent.text for ent in doc.ents]


def test_issue1612(en_tokenizer):
    doc = en_tokenizer("The black cat purrs.")
    span = doc[1:3]
    assert span.orth_ == span.text


def test_issue1654():
    nlp = Language(Vocab())
    assert not nlp.pipeline
    nlp.add_pipe(lambda doc: doc, name="1")
    nlp.add_pipe(lambda doc: doc, name="2", after="1")
    nlp.add_pipe(lambda doc: doc, name="3", after="2")
    assert nlp.pipe_names == ["1", "2", "3"]
    nlp2 = Language(Vocab())
    assert not nlp2.pipeline
    nlp2.add_pipe(lambda doc: doc, name="3")
    nlp2.add_pipe(lambda doc: doc, name="2", before="3")
    nlp2.add_pipe(lambda doc: doc, name="1", before="2")
    assert nlp2.pipe_names == ["1", "2", "3"]


@pytest.mark.parametrize("text", ["test@example.com", "john.doe@example.co.uk"])
def test_issue1698(en_tokenizer, text):
    doc = en_tokenizer(text)
    assert len(doc) == 1
    assert not doc[0].like_url


def test_issue1727():
    """Test that models with no pretrained vectors can be deserialized
    correctly after vectors are added."""
    data = numpy.ones((3, 300), dtype="f")
    vectors = Vectors(data=data, keys=["I", "am", "Matt"])
    tagger = Tagger(Vocab())
    tagger.add_label("PRP")
    with pytest.warns(UserWarning):
        tagger.begin_training()
    assert tagger.cfg.get("pretrained_dims", 0) == 0
    tagger.vocab.vectors = vectors
    with make_tempdir() as path:
        tagger.to_disk(path)
        tagger = Tagger(Vocab()).from_disk(path)
        assert tagger.cfg.get("pretrained_dims", 0) == 0


def test_issue1757():
    """Test comparison against None doesn't cause segfault."""
    doc = Doc(Vocab(), words=["a", "b", "c"])
    assert not doc[0] < None
    assert not doc[0] is None
    assert doc[0] >= None
    assert not doc[:2] < None
    assert not doc[:2] is None
    assert doc[:2] >= None
    assert not doc.vocab["a"] is None
    assert not doc.vocab["a"] < None


def test_issue1758(en_tokenizer):
    """Test that "would've" is handled by the English tokenizer exceptions."""
    tokens = en_tokenizer("would've")
    assert len(tokens) == 2
    assert tokens[0].tag_ == "MD"
    assert tokens[1].lemma_ == "have"


def test_issue1773(en_tokenizer):
    """Test that spaces don't receive a POS but no TAG. This is the root cause
    of the serialization issue reported in #1773."""
    doc = en_tokenizer("\n")
    if doc[0].pos_ == "SPACE":
        assert doc[0].tag_ != ""


def test_issue1799():
    """Test sentence boundaries are deserialized correctly, even for
    non-projective sentences."""
    heads_deps = numpy.asarray(
        [
            [1, 397],
            [4, 436],
            [2, 426],
            [1, 402],
            [0, 8206900633647566924],
            [18446744073709551615, 440],
            [18446744073709551614, 442],
        ],
        dtype="uint64",
    )
    doc = Doc(Vocab(), words="Just what I was looking for .".split())
    doc.vocab.strings.add("ROOT")
    doc = doc.from_array([HEAD, DEP], heads_deps)
    assert len(list(doc.sents)) == 1


def test_issue1807():
    """Test vocab.set_vector also adds the word to the vocab."""
    vocab = Vocab(vectors_name="test_issue1807")
    assert "hello" not in vocab
    vocab.set_vector("hello", numpy.ones((50,), dtype="f"))
    assert "hello" in vocab


def test_issue1834():
    """Test that sentence boundaries & parse/tag flags are not lost
    during serialization."""
    string = "This is a first sentence . And another one"
    doc = Doc(Vocab(), words=string.split())
    doc[6].sent_start = True
    new_doc = Doc(doc.vocab).from_bytes(doc.to_bytes())
    assert new_doc[6].sent_start
    assert not new_doc.is_parsed
    assert not new_doc.is_tagged
    doc.is_parsed = True
    doc.is_tagged = True
    new_doc = Doc(doc.vocab).from_bytes(doc.to_bytes())
    assert new_doc.is_parsed
    assert new_doc.is_tagged


def test_issue1868():
    """Test Vocab.__contains__ works with int keys."""
    vocab = Vocab()
    lex = vocab["hello"]
    assert lex.orth in vocab
    assert lex.orth_ in vocab
    assert "some string" not in vocab
    int_id = vocab.strings.add("some string")
    assert int_id not in vocab


def test_issue1883():
    matcher = Matcher(Vocab())
    matcher.add("pat1", [[{"orth": "hello"}]])
    doc = Doc(matcher.vocab, words=["hello"])
    assert len(matcher(doc)) == 1
    new_matcher = copy.deepcopy(matcher)
    new_doc = Doc(new_matcher.vocab, words=["hello"])
    assert len(new_matcher(new_doc)) == 1


@pytest.mark.parametrize("word", ["the"])
def test_issue1889(word):
    assert is_stop(word, STOP_WORDS) == is_stop(word.upper(), STOP_WORDS)


def test_issue1915():
    cfg = {"hidden_depth": 2}  # should error out
    nlp = Language()
    nlp.add_pipe(nlp.create_pipe("ner"))
    nlp.get_pipe("ner").add_label("answer")
    with pytest.raises(ValueError):
        nlp.begin_training(**cfg)


def test_issue1945():
    """Test regression in Matcher introduced in v2.0.6."""
    matcher = Matcher(Vocab())
    matcher.add("MWE", [[{"orth": "a"}, {"orth": "a"}]])
    doc = Doc(matcher.vocab, words=["a", "a", "a"])
    matches = matcher(doc)  # we should see two overlapping matches here
    assert len(matches) == 2
    assert matches[0][1:] == (0, 2)
    assert matches[1][1:] == (1, 3)


def test_issue1963(en_tokenizer):
    """Test that doc.merge() resizes doc.tensor"""
    doc = en_tokenizer("a b c d")
    doc.tensor = numpy.ones((len(doc), 128), dtype="f")
    with doc.retokenize() as retokenizer:
        retokenizer.merge(doc[0:2])
    assert len(doc) == 3
    assert doc.tensor.shape == (3, 128)


@pytest.mark.parametrize("label", ["U-JOB-NAME"])
def test_issue1967(label):
    ner = EntityRecognizer(Vocab())
    entry = ([0], ["word"], ["tag"], [0], ["dep"], [label])
    gold_parses = [(None, [(entry, None)])]
    ner.moves.get_actions(gold_parses=gold_parses)


def test_issue1971(en_vocab):
    # Possibly related to #2675 and #2671?
    matcher = Matcher(en_vocab)
    pattern = [
        {"ORTH": "Doe"},
        {"ORTH": "!", "OP": "?"},
        {"_": {"optional": True}, "OP": "?"},
        {"ORTH": "!", "OP": "?"},
    ]
    Token.set_extension("optional", default=False)
    matcher.add("TEST", [pattern])
    doc = Doc(en_vocab, words=["Hello", "John", "Doe", "!"])
    # We could also assert length 1 here, but this is more conclusive, because
    # the real problem here is that it returns a duplicate match for a match_id
    # that's not actually in the vocab!
    matches = matcher(doc)
    assert all([match_id in en_vocab.strings for match_id, start, end in matches])


def test_issue_1971_2(en_vocab):
    matcher = Matcher(en_vocab)
    pattern1 = [{"ORTH": "EUR", "LOWER": {"IN": ["eur"]}}, {"LIKE_NUM": True}]
    pattern2 = [{"LIKE_NUM": True}, {"ORTH": "EUR"}]  # {"IN": ["EUR"]}}]
    doc = Doc(en_vocab, words=["EUR", "10", "is", "10", "EUR"])
    matcher.add("TEST1", [pattern1, pattern2])
    matches = matcher(doc)
    assert len(matches) == 2


def test_issue_1971_3(en_vocab):
    """Test that pattern matches correctly for multiple extension attributes."""
    Token.set_extension("a", default=1, force=True)
    Token.set_extension("b", default=2, force=True)
    doc = Doc(en_vocab, words=["hello", "world"])
    matcher = Matcher(en_vocab)
    matcher.add("A", [[{"_": {"a": 1}}]])
    matcher.add("B", [[{"_": {"b": 2}}]])
    matches = sorted((en_vocab.strings[m_id], s, e) for m_id, s, e in matcher(doc))
    assert len(matches) == 4
    assert matches == sorted([("A", 0, 1), ("A", 1, 2), ("B", 0, 1), ("B", 1, 2)])


def test_issue_1971_4(en_vocab):
    """Test that pattern matches correctly with multiple extension attribute
    values on a single token.
    """
    Token.set_extension("ext_a", default="str_a", force=True)
    Token.set_extension("ext_b", default="str_b", force=True)
    matcher = Matcher(en_vocab)
    doc = Doc(en_vocab, words=["this", "is", "text"])
    pattern = [{"_": {"ext_a": "str_a", "ext_b": "str_b"}}] * 3
    matcher.add("TEST", [pattern])
    matches = matcher(doc)
    # Uncommenting this caused a segmentation fault
    assert len(matches) == 1
    assert matches[0] == (en_vocab.strings["TEST"], 0, 3)

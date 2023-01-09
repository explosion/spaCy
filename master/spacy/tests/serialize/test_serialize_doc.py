import copy
import pickle

import numpy
import pytest

from spacy.attrs import DEP, HEAD
from spacy.lang.en import English
from spacy.language import Language
from spacy.matcher import Matcher, PhraseMatcher
from spacy.tokens import Doc
from spacy.vectors import Vectors
from spacy.vocab import Vocab

from ..util import make_tempdir


@pytest.mark.issue(1727)
def test_issue1727():
    """Test that models with no pretrained vectors can be deserialized
    correctly after vectors are added."""
    nlp = Language(Vocab())
    data = numpy.ones((3, 300), dtype="f")
    vectors = Vectors(data=data, keys=["I", "am", "Matt"])
    tagger = nlp.create_pipe("tagger")
    tagger.add_label("PRP")
    assert tagger.cfg.get("pretrained_dims", 0) == 0
    tagger.vocab.vectors = vectors
    with make_tempdir() as path:
        tagger.to_disk(path)
        tagger = nlp.create_pipe("tagger").from_disk(path)
        assert tagger.cfg.get("pretrained_dims", 0) == 0


@pytest.mark.issue(1799)
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


@pytest.mark.issue(1834)
def test_issue1834():
    """Test that sentence boundaries & parse/tag flags are not lost
    during serialization."""
    words = ["This", "is", "a", "first", "sentence", ".", "And", "another", "one"]
    doc = Doc(Vocab(), words=words)
    doc[6].is_sent_start = True
    new_doc = Doc(doc.vocab).from_bytes(doc.to_bytes())
    assert new_doc[6].sent_start
    assert not new_doc.has_annotation("DEP")
    assert not new_doc.has_annotation("TAG")
    doc = Doc(
        Vocab(),
        words=words,
        tags=["TAG"] * len(words),
        heads=[0, 0, 0, 0, 0, 0, 6, 6, 6],
        deps=["dep"] * len(words),
    )
    new_doc = Doc(doc.vocab).from_bytes(doc.to_bytes())
    assert new_doc[6].sent_start
    assert new_doc.has_annotation("DEP")
    assert new_doc.has_annotation("TAG")


@pytest.mark.issue(1883)
def test_issue1883():
    matcher = Matcher(Vocab())
    matcher.add("pat1", [[{"orth": "hello"}]])
    doc = Doc(matcher.vocab, words=["hello"])
    assert len(matcher(doc)) == 1
    new_matcher = copy.deepcopy(matcher)
    new_doc = Doc(new_matcher.vocab, words=["hello"])
    assert len(new_matcher(new_doc)) == 1


@pytest.mark.issue(2564)
def test_issue2564():
    """Test the tagger sets has_annotation("TAG") correctly when used via Language.pipe."""
    nlp = Language()
    tagger = nlp.add_pipe("tagger")
    tagger.add_label("A")
    nlp.initialize()
    doc = nlp("hello world")
    assert doc.has_annotation("TAG")
    docs = nlp.pipe(["hello", "world"])
    piped_doc = next(docs)
    assert piped_doc.has_annotation("TAG")


@pytest.mark.issue(3248)
def test_issue3248_2():
    """Test that the PhraseMatcher can be pickled correctly."""
    nlp = English()
    matcher = PhraseMatcher(nlp.vocab)
    matcher.add("TEST1", [nlp("a"), nlp("b"), nlp("c")])
    matcher.add("TEST2", [nlp("d")])
    data = pickle.dumps(matcher)
    new_matcher = pickle.loads(data)
    assert len(new_matcher) == len(matcher)


@pytest.mark.issue(3289)
def test_issue3289():
    """Test that Language.to_bytes handles serializing a pipeline component
    with an uninitialized model."""
    nlp = English()
    nlp.add_pipe("textcat")
    bytes_data = nlp.to_bytes()
    new_nlp = English()
    new_nlp.add_pipe("textcat")
    new_nlp.from_bytes(bytes_data)


@pytest.mark.issue(3468)
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


@pytest.mark.issue(3959)
def test_issue3959():
    """Ensure that a modified pos attribute is serialized correctly."""
    nlp = English()
    doc = nlp(
        "displaCy uses JavaScript, SVG and CSS to show you how computers understand language"
    )
    assert doc[0].pos_ == ""
    doc[0].pos_ = "NOUN"
    assert doc[0].pos_ == "NOUN"
    # usually this is already True when starting from proper models instead of blank English
    with make_tempdir() as tmp_dir:
        file_path = tmp_dir / "my_doc"
        doc.to_disk(file_path)
        doc2 = nlp("")
        doc2.from_disk(file_path)
        assert doc2[0].pos_ == "NOUN"


def test_serialize_empty_doc(en_vocab):
    doc = Doc(en_vocab)
    data = doc.to_bytes()
    doc2 = Doc(en_vocab)
    doc2.from_bytes(data)
    assert len(doc) == len(doc2)
    for token1, token2 in zip(doc, doc2):
        assert token1.text == token2.text


def test_serialize_doc_roundtrip_bytes(en_vocab):
    doc = Doc(en_vocab, words=["hello", "world"])
    doc.cats = {"A": 0.5}
    doc_b = doc.to_bytes()
    new_doc = Doc(en_vocab).from_bytes(doc_b)
    assert new_doc.to_bytes() == doc_b


def test_serialize_doc_roundtrip_disk(en_vocab):
    doc = Doc(en_vocab, words=["hello", "world"])
    with make_tempdir() as d:
        file_path = d / "doc"
        doc.to_disk(file_path)
        doc_d = Doc(en_vocab).from_disk(file_path)
        assert doc.to_bytes() == doc_d.to_bytes()


def test_serialize_doc_roundtrip_disk_str_path(en_vocab):
    doc = Doc(en_vocab, words=["hello", "world"])
    with make_tempdir() as d:
        file_path = d / "doc"
        file_path = str(file_path)
        doc.to_disk(file_path)
        doc_d = Doc(en_vocab).from_disk(file_path)
        assert doc.to_bytes() == doc_d.to_bytes()


def test_serialize_doc_exclude(en_vocab):
    doc = Doc(en_vocab, words=["hello", "world"])
    doc.user_data["foo"] = "bar"
    new_doc = Doc(en_vocab).from_bytes(doc.to_bytes())
    assert new_doc.user_data["foo"] == "bar"
    new_doc = Doc(en_vocab).from_bytes(doc.to_bytes(), exclude=["user_data"])
    assert not new_doc.user_data
    new_doc = Doc(en_vocab).from_bytes(doc.to_bytes(exclude=["user_data"]))
    assert not new_doc.user_data


def test_serialize_doc_span_groups(en_vocab):
    doc = Doc(en_vocab, words=["hello", "world", "!"])
    doc.spans["content"] = [doc[0:2]]
    new_doc = Doc(en_vocab).from_bytes(doc.to_bytes())
    assert len(new_doc.spans["content"]) == 1

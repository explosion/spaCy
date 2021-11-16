import copy
import pickle

import numpy
import pytest

import spacy
from spacy.attrs import DEP, HEAD
from spacy.lang.en import English
from spacy.language import Language
from spacy.matcher import Matcher, PhraseMatcher
from spacy.tokens import Doc, DocBin
from spacy.tokens.underscore import Underscore
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


def test_serialize_doc_bin():
    doc_bin = DocBin(
        attrs=["LEMMA", "ENT_IOB", "ENT_TYPE", "NORM", "ENT_ID"], store_user_data=True
    )
    texts = ["Some text", "Lots of texts...", "..."]
    cats = {"A": 0.5}
    nlp = English()
    for doc in nlp.pipe(texts):
        doc.cats = cats
        doc.spans["start"] = [doc[0:2]]
        doc[0].norm_ = "UNUSUAL_TOKEN_NORM"
        doc[0].ent_id_ = "UNUSUAL_TOKEN_ENT_ID"
        doc_bin.add(doc)
    bytes_data = doc_bin.to_bytes()

    # Deserialize later, e.g. in a new process
    nlp = spacy.blank("en")
    doc_bin = DocBin().from_bytes(bytes_data)
    reloaded_docs = list(doc_bin.get_docs(nlp.vocab))
    for i, doc in enumerate(reloaded_docs):
        assert doc.text == texts[i]
        assert doc.cats == cats
        assert len(doc.spans) == 1
        assert doc[0].norm_ == "UNUSUAL_TOKEN_NORM"
        assert doc[0].ent_id_ == "UNUSUAL_TOKEN_ENT_ID"


def test_serialize_doc_bin_unknown_spaces(en_vocab):
    doc1 = Doc(en_vocab, words=["that", "'s"])
    assert doc1.has_unknown_spaces
    assert doc1.text == "that 's "
    doc2 = Doc(en_vocab, words=["that", "'s"], spaces=[False, False])
    assert not doc2.has_unknown_spaces
    assert doc2.text == "that's"

    doc_bin = DocBin().from_bytes(DocBin(docs=[doc1, doc2]).to_bytes())
    re_doc1, re_doc2 = doc_bin.get_docs(en_vocab)
    assert re_doc1.has_unknown_spaces
    assert re_doc1.text == "that 's "
    assert not re_doc2.has_unknown_spaces
    assert re_doc2.text == "that's"


@pytest.mark.parametrize(
    "writer_flag,reader_flag,reader_value",
    [
        (True, True, "bar"),
        (True, False, "bar"),
        (False, True, "nothing"),
        (False, False, "nothing"),
    ],
)
def test_serialize_custom_extension(en_vocab, writer_flag, reader_flag, reader_value):
    """Test that custom extensions are correctly serialized in DocBin."""
    Doc.set_extension("foo", default="nothing")
    doc = Doc(en_vocab, words=["hello", "world"])
    doc._.foo = "bar"
    doc_bin_1 = DocBin(store_user_data=writer_flag)
    doc_bin_1.add(doc)
    doc_bin_bytes = doc_bin_1.to_bytes()
    doc_bin_2 = DocBin(store_user_data=reader_flag).from_bytes(doc_bin_bytes)
    doc_2 = list(doc_bin_2.get_docs(en_vocab))[0]
    assert doc_2._.foo == reader_value
    Underscore.doc_extensions = {}

import pytest

import spacy
from spacy.lang.en import English
from spacy.tokens import Doc, DocBin
from spacy.tokens.underscore import Underscore


@pytest.mark.issue(4367)
def test_issue4367():
    """Test that docbin init goes well"""
    DocBin()
    DocBin(attrs=["LEMMA"])
    DocBin(attrs=["LEMMA", "ENT_IOB", "ENT_TYPE"])


@pytest.mark.issue(4528)
def test_issue4528(en_vocab):
    """Test that user_data is correctly serialized in DocBin."""
    doc = Doc(en_vocab, words=["hello", "world"])
    doc.user_data["foo"] = "bar"
    # This is how extension attribute values are stored in the user data
    doc.user_data[("._.", "foo", None, None)] = "bar"
    doc_bin = DocBin(store_user_data=True)
    doc_bin.add(doc)
    doc_bin_bytes = doc_bin.to_bytes()
    new_doc_bin = DocBin(store_user_data=True).from_bytes(doc_bin_bytes)
    new_doc = list(new_doc_bin.get_docs(en_vocab))[0]
    assert new_doc.user_data["foo"] == "bar"
    assert new_doc.user_data[("._.", "foo", None, None)] == "bar"


@pytest.mark.issue(5141)
def test_issue5141(en_vocab):
    """Ensure an empty DocBin does not crash on serialization"""
    doc_bin = DocBin(attrs=["DEP", "HEAD"])
    assert list(doc_bin.get_docs(en_vocab)) == []
    doc_bin_bytes = doc_bin.to_bytes()
    doc_bin_2 = DocBin().from_bytes(doc_bin_bytes)
    assert list(doc_bin_2.get_docs(en_vocab)) == []


def test_serialize_doc_bin():
    doc_bin = DocBin(
        attrs=["LEMMA", "ENT_IOB", "ENT_TYPE", "NORM", "ENT_ID"], store_user_data=True
    )
    texts = ["Some text", "Lots of texts...", "..."]
    cats = {"A": 0.5}
    nlp = English()
    for doc in nlp.pipe(texts):
        doc.cats = cats
        span = doc[0:2]
        span.label_ = "UNUSUAL_SPAN_LABEL"
        span.id_ = "UNUSUAL_SPAN_ID"
        span.kb_id_ = "UNUSUAL_SPAN_KB_ID"
        doc.spans["start"] = [span]
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
        assert doc.spans["start"][0].label_ == "UNUSUAL_SPAN_LABEL"
        assert doc.spans["start"][0].id_ == "UNUSUAL_SPAN_ID"
        assert doc.spans["start"][0].kb_id_ == "UNUSUAL_SPAN_KB_ID"
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

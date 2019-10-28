# coding: utf8
from __future__ import unicode_literals

from spacy.tokens import Doc, DocBin


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

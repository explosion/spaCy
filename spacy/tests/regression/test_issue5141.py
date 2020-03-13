from spacy.tokens import DocBin


def test_issue5141(en_vocab):
    """ Ensure an empty DocBin does not crash on serialization """
    doc_bin = DocBin(attrs=["DEP", "HEAD"])
    assert list(doc_bin.get_docs(en_vocab)) == []
    doc_bin_bytes = doc_bin.to_bytes()

    doc_bin_2 = DocBin().from_bytes(doc_bin_bytes)
    assert list(doc_bin_2.get_docs(en_vocab)) == []

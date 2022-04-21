from spacy.tokens import Doc, Span


def test_json_to_doc(doc):
    new_doc = Doc.from_json(doc.vocab, doc.to_json())
    new_tokens = [token for token in new_doc]
    assert new_doc.text == doc.text
    assert len(new_tokens) == len([token for token in doc])
    assert doc.text == "c d e "
    assert len(new_tokens) == 3
    assert new_tokens[0].pos_ == "VERB"
    assert new_tokens[0].tag_ == "VBP"
    assert new_tokens[0].dep_ == "ROOT"
    assert len(new_doc.ents) == 1
    assert new_doc.ents[0].start_char == 2
    assert new_doc.ents[0].end_char == 3
    assert new_doc.ents[0].start == 1
    assert new_doc.ents[0].end == 2
    assert new_doc.ents[0].label_ == "ORG"


def test_json_to_doc_underscore(doc):
    Doc.set_extension("json_test1", default=False)
    Doc.set_extension("json_test2", default=False)

    doc._.json_test1 = "hello world"
    doc._.json_test2 = [1, 2, 3]
    new_doc = Doc.from_json(
        doc.vocab, doc.to_json(underscore=["json_test1", "json_test2"])
    )
    assert all([new_doc.has_extension(f"json_test{i}") for i in range(1, 3)])
    assert new_doc._.json_test1 == "hello world"
    assert new_doc._.json_test2 == [1, 2, 3]


def test_json_to_doc_span(doc):
    """Test that Doc.from_json() includes correct.spans."""
    doc.spans["test"] = [Span(doc, 0, 2, "test"), Span(doc, 0, 1, "test")]
    new_doc = Doc.from_json(doc.vocab, doc.to_json())
    assert len(new_doc.spans) == 1
    assert len(new_doc.spans["test"]) == 2
    assert new_doc.spans["test"][0].start == 0


def test_json_to_doc_cats(doc):
    """Test that Doc.from_json() includes correct .cats."""
    cats = {"A": 0.3, "B": 0.7}
    doc.cats = cats
    new_doc = Doc.from_json(doc.vocab, doc.to_json())
    assert new_doc.cats == cats

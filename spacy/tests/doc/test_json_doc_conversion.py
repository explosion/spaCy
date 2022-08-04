import pytest
import spacy
from spacy import schemas
from spacy.tokens import Doc, Span


@pytest.fixture()
def doc(en_vocab):
    words = ["c", "d", "e"]
    pos = ["VERB", "NOUN", "NOUN"]
    tags = ["VBP", "NN", "NN"]
    heads = [0, 0, 1]
    deps = ["ROOT", "dobj", "dobj"]
    ents = ["O", "B-ORG", "O"]
    morphs = ["Feat1=A", "Feat1=B", "Feat1=A|Feat2=D"]

    return Doc(
        en_vocab,
        words=words,
        pos=pos,
        tags=tags,
        heads=heads,
        deps=deps,
        ents=ents,
        morphs=morphs,
    )


@pytest.fixture()
def doc_without_deps(en_vocab):
    words = ["c", "d", "e"]
    pos = ["VERB", "NOUN", "NOUN"]
    tags = ["VBP", "NN", "NN"]
    ents = ["O", "B-ORG", "O"]
    morphs = ["Feat1=A", "Feat1=B", "Feat1=A|Feat2=D"]

    return Doc(
        en_vocab,
        words=words,
        pos=pos,
        tags=tags,
        ents=ents,
        morphs=morphs,
        sent_starts=[True, False, True],
    )


def test_doc_to_json(doc):
    json_doc = doc.to_json()
    assert json_doc["text"] == "c d e "
    assert len(json_doc["tokens"]) == 3
    assert json_doc["tokens"][0]["pos"] == "VERB"
    assert json_doc["tokens"][0]["tag"] == "VBP"
    assert json_doc["tokens"][0]["dep"] == "ROOT"
    assert len(json_doc["ents"]) == 1
    assert json_doc["ents"][0]["start"] == 2  # character offset!
    assert json_doc["ents"][0]["end"] == 3  # character offset!
    assert json_doc["ents"][0]["label"] == "ORG"
    assert not schemas.validate(schemas.DocJSONSchema, json_doc)


def test_doc_to_json_underscore(doc):
    Doc.set_extension("json_test1", default=False)
    Doc.set_extension("json_test2", default=False)
    doc._.json_test1 = "hello world"
    doc._.json_test2 = [1, 2, 3]
    json_doc = doc.to_json(underscore=["json_test1", "json_test2"])
    assert "_" in json_doc
    assert json_doc["_"]["json_test1"] == "hello world"
    assert json_doc["_"]["json_test2"] == [1, 2, 3]
    assert not schemas.validate(schemas.DocJSONSchema, json_doc)


def test_doc_to_json_underscore_error_attr(doc):
    """Test that Doc.to_json() raises an error if a custom attribute doesn't
    exist in the ._ space."""
    with pytest.raises(ValueError):
        doc.to_json(underscore=["json_test3"])


def test_doc_to_json_underscore_error_serialize(doc):
    """Test that Doc.to_json() raises an error if a custom attribute value
    isn't JSON-serializable."""
    Doc.set_extension("json_test4", method=lambda doc: doc.text)
    with pytest.raises(ValueError):
        doc.to_json(underscore=["json_test4"])


def test_doc_to_json_span(doc):
    """Test that Doc.to_json() includes spans"""
    doc.spans["test"] = [Span(doc, 0, 2, "test"), Span(doc, 0, 1, "test")]
    json_doc = doc.to_json()
    assert "spans" in json_doc
    assert len(json_doc["spans"]) == 1
    assert len(json_doc["spans"]["test"]) == 2
    assert json_doc["spans"]["test"][0]["start"] == 0
    assert not schemas.validate(schemas.DocJSONSchema, json_doc)


def test_json_to_doc(doc):
    new_doc = Doc(doc.vocab).from_json(doc.to_json(), validate=True)
    new_tokens = [token for token in new_doc]
    assert new_doc.text == doc.text == "c d e "
    assert len(new_tokens) == len([token for token in doc]) == 3
    assert new_tokens[0].pos == doc[0].pos
    assert new_tokens[0].tag == doc[0].tag
    assert new_tokens[0].dep == doc[0].dep
    assert new_tokens[0].head.idx == doc[0].head.idx
    assert new_tokens[0].lemma == doc[0].lemma
    assert len(new_doc.ents) == 1
    assert new_doc.ents[0].start == 1
    assert new_doc.ents[0].end == 2
    assert new_doc.ents[0].label_ == "ORG"


def test_json_to_doc_underscore(doc):
    if not Doc.has_extension("json_test1"):
        Doc.set_extension("json_test1", default=False)
    if not Doc.has_extension("json_test2"):
        Doc.set_extension("json_test2", default=False)

    doc._.json_test1 = "hello world"
    doc._.json_test2 = [1, 2, 3]
    json_doc = doc.to_json(underscore=["json_test1", "json_test2"])
    new_doc = Doc(doc.vocab).from_json(json_doc, validate=True)
    assert all([new_doc.has_extension(f"json_test{i}") for i in range(1, 3)])
    assert new_doc._.json_test1 == "hello world"
    assert new_doc._.json_test2 == [1, 2, 3]


def test_json_to_doc_spans(doc):
    """Test that Doc.from_json() includes correct.spans."""
    doc.spans["test"] = [
        Span(doc, 0, 2, label="test"),
        Span(doc, 0, 1, label="test", kb_id=7),
    ]
    json_doc = doc.to_json()
    new_doc = Doc(doc.vocab).from_json(json_doc, validate=True)
    assert len(new_doc.spans) == 1
    assert len(new_doc.spans["test"]) == 2
    for i in range(2):
        assert new_doc.spans["test"][i].start == doc.spans["test"][i].start
        assert new_doc.spans["test"][i].end == doc.spans["test"][i].end
        assert new_doc.spans["test"][i].label == doc.spans["test"][i].label
        assert new_doc.spans["test"][i].kb_id == doc.spans["test"][i].kb_id


def test_json_to_doc_sents(doc, doc_without_deps):
    """Test that Doc.from_json() includes correct.sents."""
    for test_doc in (doc, doc_without_deps):
        json_doc = test_doc.to_json()
        new_doc = Doc(doc.vocab).from_json(json_doc, validate=True)
        assert [sent.text for sent in test_doc.sents] == [
            sent.text for sent in new_doc.sents
        ]
        assert [token.is_sent_start for token in test_doc] == [
            token.is_sent_start for token in new_doc
        ]


def test_json_to_doc_cats(doc):
    """Test that Doc.from_json() includes correct .cats."""
    cats = {"A": 0.3, "B": 0.7}
    doc.cats = cats
    json_doc = doc.to_json()
    new_doc = Doc(doc.vocab).from_json(json_doc, validate=True)
    assert new_doc.cats == cats


def test_json_to_doc_spaces():
    """Test that Doc.from_json() preserves spaces correctly."""
    doc = spacy.blank("en")("This is just brilliant.")
    json_doc = doc.to_json()
    new_doc = Doc(doc.vocab).from_json(json_doc, validate=True)
    assert doc.text == new_doc.text


def test_json_to_doc_attribute_consistency(doc):
    """Test that Doc.from_json() raises an exception if tokens don't all have the same set of properties."""
    doc_json = doc.to_json()
    doc_json["tokens"][1].pop("morph")
    with pytest.raises(ValueError):
        Doc(doc.vocab).from_json(doc_json)


def test_json_to_doc_validation_error(doc):
    """Test that Doc.from_json() raises an exception when validating invalid input."""
    doc_json = doc.to_json()
    doc_json.pop("tokens")
    with pytest.raises(ValueError):
        Doc(doc.vocab).from_json(doc_json, validate=True)

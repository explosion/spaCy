import pytest
import spacy
from spacy import schemas
from spacy.tokens import Doc, Span, Token
import srsly
from .test_underscore import clean_underscore  # noqa: F401


@pytest.fixture()
def doc(en_vocab):
    words = ["c", "d", "e"]
    spaces = [True, True, True]
    pos = ["VERB", "NOUN", "NOUN"]
    tags = ["VBP", "NN", "NN"]
    heads = [0, 0, 1]
    deps = ["ROOT", "dobj", "dobj"]
    ents = ["O", "B-ORG", "O"]
    morphs = ["Feat1=A", "Feat1=B", "Feat1=A|Feat2=D"]

    return Doc(
        en_vocab,
        words=words,
        spaces=spaces,
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


@pytest.fixture()
def doc_json():
    return {
        "text": "c d e ",
        "ents": [{"start": 2, "end": 3, "label": "ORG"}],
        "sents": [{"start": 0, "end": 5}],
        "tokens": [
            {
                "id": 0,
                "start": 0,
                "end": 1,
                "tag": "VBP",
                "pos": "VERB",
                "morph": "Feat1=A",
                "dep": "ROOT",
                "head": 0,
            },
            {
                "id": 1,
                "start": 2,
                "end": 3,
                "tag": "NN",
                "pos": "NOUN",
                "morph": "Feat1=B",
                "dep": "dobj",
                "head": 0,
            },
            {
                "id": 2,
                "start": 4,
                "end": 5,
                "tag": "NN",
                "pos": "NOUN",
                "morph": "Feat1=A|Feat2=D",
                "dep": "dobj",
                "head": 1,
            },
        ],
    }


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
    assert len(schemas.validate(schemas.DocJSONSchema, json_doc)) == 0
    assert srsly.json_loads(srsly.json_dumps(json_doc)) == json_doc


def test_doc_to_json_underscore(doc):
    Doc.set_extension("json_test1", default=False)
    Doc.set_extension("json_test2", default=False)
    doc._.json_test1 = "hello world"
    doc._.json_test2 = [1, 2, 3]

    json_doc = doc.to_json(underscore=["json_test1", "json_test2"])
    assert "_" in json_doc
    assert json_doc["_"]["json_test1"] == "hello world"
    assert json_doc["_"]["json_test2"] == [1, 2, 3]
    assert len(schemas.validate(schemas.DocJSONSchema, json_doc)) == 0
    assert srsly.json_loads(srsly.json_dumps(json_doc)) == json_doc


def test_doc_to_json_with_token_span_attributes(doc):
    Doc.set_extension("json_test1", default=False)
    Doc.set_extension("json_test2", default=False)
    Token.set_extension("token_test", default=False)
    Span.set_extension("span_test", default=False)

    doc._.json_test1 = "hello world"
    doc._.json_test2 = [1, 2, 3]
    doc[0:1]._.span_test = "span_attribute"
    doc[0:2]._.span_test = "span_attribute_2"
    doc[0]._.token_test = 117
    doc[1]._.token_test = 118
    doc.spans["span_group"] = [doc[0:1]]
    json_doc = doc.to_json(
        underscore=["json_test1", "json_test2", "token_test", "span_test"]
    )

    assert "_" in json_doc
    assert json_doc["_"]["json_test1"] == "hello world"
    assert json_doc["_"]["json_test2"] == [1, 2, 3]
    assert "underscore_token" in json_doc
    assert "underscore_span" in json_doc
    assert json_doc["underscore_token"]["token_test"][0]["value"] == 117
    assert json_doc["underscore_token"]["token_test"][1]["value"] == 118
    assert json_doc["underscore_span"]["span_test"][0]["value"] == "span_attribute"
    assert json_doc["underscore_span"]["span_test"][1]["value"] == "span_attribute_2"
    assert len(schemas.validate(schemas.DocJSONSchema, json_doc)) == 0
    assert srsly.json_loads(srsly.json_dumps(json_doc)) == json_doc


def test_doc_to_json_with_custom_user_data(doc):
    Doc.set_extension("json_test", default=False)
    Token.set_extension("token_test", default=False)
    Span.set_extension("span_test", default=False)

    doc._.json_test = "hello world"
    doc[0:1]._.span_test = "span_attribute"
    doc[0]._.token_test = 117
    json_doc = doc.to_json(underscore=["json_test", "token_test", "span_test"])
    doc.user_data["user_data_test"] = 10
    doc.user_data[("user_data_test2", True)] = 10

    assert "_" in json_doc
    assert json_doc["_"]["json_test"] == "hello world"
    assert "underscore_token" in json_doc
    assert "underscore_span" in json_doc
    assert json_doc["underscore_token"]["token_test"][0]["value"] == 117
    assert json_doc["underscore_span"]["span_test"][0]["value"] == "span_attribute"
    assert len(schemas.validate(schemas.DocJSONSchema, json_doc)) == 0
    assert srsly.json_loads(srsly.json_dumps(json_doc)) == json_doc


def test_doc_to_json_with_token_span_same_identifier(doc):
    Doc.set_extension("my_ext", default=False)
    Token.set_extension("my_ext", default=False)
    Span.set_extension("my_ext", default=False)

    doc._.my_ext = "hello world"
    doc[0:1]._.my_ext = "span_attribute"
    doc[0]._.my_ext = 117
    json_doc = doc.to_json(underscore=["my_ext"])

    assert "_" in json_doc
    assert json_doc["_"]["my_ext"] == "hello world"
    assert "underscore_token" in json_doc
    assert "underscore_span" in json_doc
    assert json_doc["underscore_token"]["my_ext"][0]["value"] == 117
    assert json_doc["underscore_span"]["my_ext"][0]["value"] == "span_attribute"
    assert len(schemas.validate(schemas.DocJSONSchema, json_doc)) == 0
    assert srsly.json_loads(srsly.json_dumps(json_doc)) == json_doc


def test_doc_to_json_with_token_attributes_missing(doc):
    Token.set_extension("token_test", default=False)
    Span.set_extension("span_test", default=False)

    doc[0:1]._.span_test = "span_attribute"
    doc[0]._.token_test = 117
    json_doc = doc.to_json(underscore=["span_test"])

    assert "underscore_span" in json_doc
    assert json_doc["underscore_span"]["span_test"][0]["value"] == "span_attribute"
    assert "underscore_token" not in json_doc
    assert len(schemas.validate(schemas.DocJSONSchema, json_doc)) == 0


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
    assert len(schemas.validate(schemas.DocJSONSchema, json_doc)) == 0


def test_json_to_doc(doc):
    json_doc = doc.to_json()
    json_doc = srsly.json_loads(srsly.json_dumps(json_doc))
    new_doc = Doc(doc.vocab).from_json(json_doc, validate=True)
    assert new_doc.text == doc.text == "c d e "
    assert len(new_doc) == len(doc) == 3
    assert new_doc[0].pos == doc[0].pos
    assert new_doc[0].tag == doc[0].tag
    assert new_doc[0].dep == doc[0].dep
    assert new_doc[0].head.idx == doc[0].head.idx
    assert new_doc[0].lemma == doc[0].lemma
    assert len(new_doc.ents) == 1
    assert new_doc.ents[0].start == 1
    assert new_doc.ents[0].end == 2
    assert new_doc.ents[0].label_ == "ORG"
    assert doc.to_bytes() == new_doc.to_bytes()


def test_json_to_doc_compat(doc, doc_json):
    new_doc = Doc(doc.vocab).from_json(doc_json, validate=True)
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
    Doc.set_extension("json_test1", default=False)
    Doc.set_extension("json_test2", default=False)
    doc._.json_test1 = "hello world"
    doc._.json_test2 = [1, 2, 3]
    json_doc = doc.to_json(underscore=["json_test1", "json_test2"])
    new_doc = Doc(doc.vocab).from_json(json_doc, validate=True)
    assert all([new_doc.has_extension(f"json_test{i}") for i in range(1, 3)])
    assert new_doc._.json_test1 == "hello world"
    assert new_doc._.json_test2 == [1, 2, 3]
    assert doc.to_bytes() == new_doc.to_bytes()


def test_json_to_doc_with_token_span_attributes(doc):
    Doc.set_extension("json_test1", default=False)
    Doc.set_extension("json_test2", default=False)
    Token.set_extension("token_test", default=False)
    Span.set_extension("span_test", default=False)
    doc._.json_test1 = "hello world"
    doc._.json_test2 = [1, 2, 3]
    doc[0:1]._.span_test = "span_attribute"
    doc[0:2]._.span_test = "span_attribute_2"
    doc[0]._.token_test = 117
    doc[1]._.token_test = 118

    json_doc = doc.to_json(
        underscore=["json_test1", "json_test2", "token_test", "span_test"]
    )
    json_doc = srsly.json_loads(srsly.json_dumps(json_doc))
    new_doc = Doc(doc.vocab).from_json(json_doc, validate=True)

    assert all([new_doc.has_extension(f"json_test{i}") for i in range(1, 3)])
    assert new_doc._.json_test1 == "hello world"
    assert new_doc._.json_test2 == [1, 2, 3]
    assert new_doc[0]._.token_test == 117
    assert new_doc[1]._.token_test == 118
    assert new_doc[0:1]._.span_test == "span_attribute"
    assert new_doc[0:2]._.span_test == "span_attribute_2"
    assert new_doc.user_data == doc.user_data
    assert new_doc.to_bytes(exclude=["user_data"]) == doc.to_bytes(
        exclude=["user_data"]
    )


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

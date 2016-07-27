from __future__ import unicode_literals
import pytest

from spacy.tokens import Doc

def equal(doc1, doc2):
    # tokens
    assert [ t.orth for t in doc1 ] == [ t.orth for t in doc2 ]

    # tags
    assert [ t.pos for t in doc1 ] == [ t.pos for t in doc2 ]
    assert [ t.tag for t in doc1 ] == [ t.tag for t in doc2 ]

    # parse
    assert [ t.head.i for t in doc1 ] == [ t.head.i for t in doc2 ]
    assert [ t.dep for t in doc1 ] == [ t.dep for t in doc2 ]
    if doc1.is_parsed and doc2.is_parsed:
        assert [ s for s in doc1.sents ] == [ s for s in doc2.sents ]

    # entities
    assert [ t.ent_type for t in doc1 ] == [ t.ent_type for t in doc2 ]
    assert [ t.ent_iob for t in doc1 ] == [ t.ent_iob for t in doc2 ]
    assert [ ent for ent in doc1.ents ] == [ ent for ent in doc2.ents ]


@pytest.mark.models
def test_serialize_tokens(EN):
    doc1 = EN(u'This is a test sentence.',tag=False, parse=False, entity=False)

    doc2 = Doc(EN.vocab).from_bytes(doc1.to_bytes())
    equal(doc1, doc2)


@pytest.mark.models
def test_serialize_tokens_tags(EN):
    doc1 = EN(u'This is a test sentence.',tag=True, parse=False, entity=False)
    doc2 = Doc(EN.vocab).from_bytes(doc1.to_bytes())
    equal(doc1, doc2)


@pytest.mark.models
def test_serialize_tokens_parse(EN):
    doc1 = EN(u'This is a test sentence.',tag=False, parse=True, entity=False)

    doc2 = Doc(EN.vocab).from_bytes(doc1.to_bytes())
    equal(doc1, doc2)


@pytest.mark.models
def test_serialize_tokens_ner(EN):
    doc1 = EN(u'This is a test sentence.', tag=False, parse=False, entity=True)

    doc2 = Doc(EN.vocab).from_bytes(doc1.to_bytes())
    equal(doc1, doc2)


@pytest.mark.models
def test_serialize_tokens_tags_parse(EN):
    doc1 = EN(u'This is a test sentence.', tag=True, parse=True, entity=False)

    doc2 = Doc(EN.vocab).from_bytes(doc1.to_bytes())
    equal(doc1, doc2)


@pytest.mark.models
def test_serialize_tokens_tags_ner(EN):
    doc1 = EN(u'This is a test sentence.', tag=True, parse=False, entity=True)

    doc2 = Doc(EN.vocab).from_bytes(doc1.to_bytes())
    equal(doc1, doc2)


@pytest.mark.models
def test_serialize_tokens_ner_parse(EN):
    doc1 = EN(u'This is a test sentence.', tag=False, parse=True, entity=True)

    doc2 = Doc(EN.vocab).from_bytes(doc1.to_bytes())
    equal(doc1, doc2)


@pytest.mark.models
def test_serialize_tokens_tags_parse_ner(EN):
    doc1 = EN(u'This is a test sentence.', tag=True, parse=True, entity=True)

    doc2 = Doc(EN.vocab).from_bytes(doc1.to_bytes())
    equal(doc1, doc2)

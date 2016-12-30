from __future__ import unicode_literals
import pytest

from spacy.tokens import Doc
import spacy.en
from spacy.serialize.packer import Packer


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


def test_serialize_empty_doc():
    vocab = spacy.en.English.Defaults.create_vocab()
    doc = Doc(vocab)
    packer = Packer(vocab, {})
    b = packer.pack(doc)
    assert b == b''
    loaded = Doc(vocab).from_bytes(b)
    assert len(loaded) == 0


def test_serialize_after_adding_entity():
    # Re issue #514
    vocab = spacy.en.English.Defaults.create_vocab()
    entity_recognizer = spacy.en.English.Defaults.create_entity()

    doc = Doc(vocab, words=u'This is a sentence about pasta .'.split())
    entity_recognizer.add_label('Food')
    entity_recognizer(doc)

    label_id = vocab.strings[u'Food']
    doc.ents = [(label_id, 5,6)]

    assert [(ent.label_, ent.text) for ent in doc.ents] == [(u'Food', u'pasta')]

    byte_string = doc.to_bytes()


@pytest.mark.models
def test_serialize_after_adding_entity(EN):
    EN.entity.add_label(u'Food')
    doc = EN(u'This is a sentence about pasta.')
    label_id = EN.vocab.strings[u'Food']
    doc.ents = [(label_id, 5,6)]
    byte_string = doc.to_bytes()
    doc2 = Doc(EN.vocab).from_bytes(byte_string)
    assert [(ent.label_, ent.text) for ent in doc2.ents] == [(u'Food', u'pasta')]

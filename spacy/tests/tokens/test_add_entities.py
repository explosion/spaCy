from __future__ import unicode_literals
import spacy
from spacy.vocab import Vocab
from spacy.matcher import Matcher
from spacy.tokens.doc import Doc
from spacy.attrs import *
from spacy.pipeline import EntityRecognizer

import pytest


@pytest.fixture(scope="module")
def en_vocab():
    return spacy.get_lang_class('en').Defaults.create_vocab()


@pytest.fixture(scope="module")
def entity_recognizer(en_vocab):
    return EntityRecognizer(en_vocab, features=[(2,), (3,)])

@pytest.fixture
def animal(en_vocab):
    return nlp.vocab.strings[u"ANIMAL"]


@pytest.fixture
def doc(en_vocab, entity_recognizer):
    doc = Doc(en_vocab, words=[u"this",  u"is", u"a", u"lion"])
    entity_recognizer(doc)
    return doc


def test_set_ents_iob(doc):
    assert len(list(doc.ents)) == 0
    tags = [w.ent_iob_ for w in doc]
    assert tags == (['O'] * len(doc))
    doc.ents = [(doc.vocab.strings['ANIMAL'], 3, 4)]
    tags = [w.ent_iob_ for w in doc]
    assert tags == ['O', 'O', 'O', 'B']
    doc.ents = [(doc.vocab.strings['WORD'], 0, 2)]
    tags = [w.ent_iob_ for w in doc]
    assert tags == ['B', 'I', 'O', 'O']

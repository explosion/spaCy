from __future__ import unicode_literals
from spacy.en import English
from spacy.en.attrs import IS_ALPHA, IS_ASCII, IS_DIGIT, IS_LOWER, IS_PUNCT
from spacy.en.attrs import IS_SPACE, IS_TITLE, IS_UPPER, LIKE_URL, LIKE_NUM
from spacy.en.attrs import IS_STOP

import pytest

nlp = English()
@pytest.fixture
def token():
    tokens = nlp(u'Give it back! He pleaded.')
    return tokens[0]


def test_strings(token):
    assert token.orth_ == 'Give'
    assert token.lower_ == 'give'
    assert token.shape_ == 'Xxxx'
    assert token.prefix_ == 'G'
    assert token.suffix_ == 'ive'
    assert token.lemma_ == 'give'
    assert token.pos_ == 'VERB'
    assert token.tag_ == 'VB'
    assert token.dep_ == 'ROOT'


def test_flags(token):
    assert token.check_flag(IS_ALPHA)
    assert not token.check_flag(IS_DIGIT)
    # TODO: Test more of these, esp. if a bug is found


def test_single_token_string():
    nlp = English()
    tokens = nlp(u'foobar')
    assert tokens[0].string == 'foobar'



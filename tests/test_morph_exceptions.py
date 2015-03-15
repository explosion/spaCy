from __future__ import unicode_literals
from spacy.en import English

import pytest

from spacy.en import English


@pytest.fixture
def EN():
    return English()


@pytest.fixture
def morph_exc():
    return {
            'PRP$': {'his': {'L': '-PRP-', 'person': 3, 'case': 2}},
           }

def test_load_exc(EN, morph_exc):
    EN.tagger.load_morph_exceptions(morph_exc)
    tokens = EN('I like his style.', tag=True)
    his = tokens[2]
    assert his.tag_ == 'PRP$'
    assert his.lemma_ == '-PRP-'

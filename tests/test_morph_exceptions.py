from __future__ import unicode_literals
from spacy.en import English

import pytest

from spacy.en import English


@pytest.fixture
def EN():
    return English(pos_tag=True, parse=False)


@pytest.fixture
def morph_exc():
    return {
            'PRP$': {'his': {'L': '-PRP-', 'person': 3, 'case': 2}},
           }

def test_load_exc(EN, morph_exc):
    EN.pos_tagger.morphologizer.load_exceptions(morph_exc)
    tokens = EN('I like his style.', pos_tag=True)
    his = tokens[2]
    assert his.pos == 'PRP$'
    assert his.lemma == '-PRP-'

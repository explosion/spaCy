from __future__ import unicode_literals
from spacy.en import EN

import pytest

@pytest.fixture
def morph_exc():
    return {
            'PRP$': {'his': {'L': '-PRP-', 'person': 3, 'case': 2}},
           }

def test_load_exc(morph_exc):
    EN.load()
    EN.morphologizer.load_exceptions(morph_exc)
    tokens = EN.tokenize('I like his style.')
    EN.set_pos(tokens)
    his = tokens[2]
    assert his.pos == 'PRP$'
    assert his.lemma == '-PRP-'

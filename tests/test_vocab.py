from __future__ import unicode_literals

from spacy.en import EN


def test_neq():
    addr = EN.lexicon['Hello']
    assert EN.lexicon['bye']['sic'] != addr['sic']


def test_eq():
    addr = EN.lexicon['Hello']
    assert EN.lexicon['Hello']['sic'] == addr['sic']


def test_case_neq():
    addr = EN.lexicon['Hello']
    assert EN.lexicon['hello']['sic'] != addr['sic']


def test_punct_neq():
    addr = EN.lexicon['Hello']
    assert EN.lexicon['Hello,']['sic'] != addr['sic']

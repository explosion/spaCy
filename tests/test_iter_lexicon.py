import pytest

from spacy.en import EN

def test_range_iter():
    EN.load()
    for i in range(len(EN.lexicon)):
        lex = EN.lexicon[i]


def test_iter():
    EN.load()
    i = 0
    for lex in EN.lexicon:
        i += 1

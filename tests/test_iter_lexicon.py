import pytest

from spacy.en import English

@pytest.fixture
def EN():
    return English()

def test_range_iter(EN):
    for i in range(len(EN.vocab)):
        lex = EN.vocab[i]


def test_iter(EN):
    i = 0
    for lex in EN.vocab:
        i += 1

from spacy.en import EN
import pytest


@pytest.fixture
def tagged():
    EN.load()
    string = u'Bananas in pyjamas are geese.'
    tokens = EN.tokenize(string)
    EN.set_pos(tokens)
    return tokens


@pytest.fixture
def lemmas(tagged):
    return [t.lemma for t in tagged]


def test_lemmas(lemmas):
    assert lemmas[0] == 'banana'
    assert lemmas[1] == 'in'
    assert lemmas[2] == 'pyjama'
    assert lemmas[3] == 'be'
    assert lemmas[4] == 'goose'

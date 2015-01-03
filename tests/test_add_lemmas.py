from spacy.en import English
import pytest


@pytest.fixture
def EN():
    return English()

@pytest.fixture
def tagged(EN):
    string = u'Bananas in pyjamas are geese.'
    tokens = EN(string, tag=True)
    return tokens


@pytest.fixture
def lemmas(tagged):
    return [t.lemma for t in tagged]


def test_lemmas(lemmas, tagged):
    assert lemmas[0] == 'banana'
    assert lemmas[1] == 'in'
    assert lemmas[2] == 'pyjama'
    assert lemmas[3] == 'be'
    if tagged[2].fine_pos == tagged[4].fine_pos:
        assert lemmas[4] == 'goose'

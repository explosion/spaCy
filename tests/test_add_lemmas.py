from spacy.en import English
import pytest

@pytest.fixture
def EN():
    return English(pos_tag=True, parse=False)

@pytest.fixture
def tagged(EN):
    string = u'Bananas in pyjamas are geese.'
    tokens = EN(string, pos_tag=True)
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

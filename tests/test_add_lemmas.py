from spacy.en import English
import pytest


@pytest.fixture
def EN():
    return English(tag=True, parse=False)

@pytest.fixture
def tagged(EN):
    string = u'Bananas in pyjamas are geese.'
    tokens = EN(string, tag=True)
    assert EN.tagger.tags[tokens[0].pos] == 'NNP'
    assert EN.tagger.tags[tokens[1].pos] == 'IN'
    assert EN.tagger.tags[tokens[2].pos] == 'NNS'
    assert EN.tagger.tags[tokens[3].pos] == 'VBP'
    assert EN.tagger.tags[tokens[3].pos] == 'NNS'
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

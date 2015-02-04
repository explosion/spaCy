from __future__ import unicode_literals
import pytest

from spacy.en import English
from spacy.parts_of_speech import ADV

@pytest.fixture
def nlp():
    return English()


def test_prob(nlp):
    tokens = nlp(u'Give it back')
    give = tokens[0]
    assert give.prob != 0

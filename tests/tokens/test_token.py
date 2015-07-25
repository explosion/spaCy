from __future__ import unicode_literals
import pytest

from spacy.parts_of_speech import ADV


@pytest.mark.models
def test_prob(EN):
    tokens = EN(u'Give it back', parse=False)
    give = tokens[0]
    assert give.prob != 0

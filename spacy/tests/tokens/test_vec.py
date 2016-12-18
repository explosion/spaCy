from __future__ import unicode_literals

from spacy.en import English

import pytest

@pytest.mark.models
def test_vec(EN):
    hype = EN.vocab['hype']
    assert hype.orth_ == 'hype'
    assert -0.7 >= hype.vector[0] > -0.8


@pytest.mark.models
def test_capitalized(EN):
    hype = EN.vocab['Hype']
    assert hype.orth_ == 'Hype'
    assert -0.7 >= hype.vector[0] > -0.8

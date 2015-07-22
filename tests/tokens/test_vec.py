from __future__ import unicode_literals

from spacy.en import English

import pytest

@pytest.mark.vectors
def test_vec(EN):
    hype = EN.vocab['hype']
    assert hype.orth_ == 'hype'
    assert 0.08 >= hype.repvec[0] > 0.07


@pytest.mark.vectors
def test_capitalized(EN):
    hype = EN.vocab['Hype']
    assert hype.orth_ == 'Hype'
    assert 0.08 >= hype.repvec[0] > 0.07

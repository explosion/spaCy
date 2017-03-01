# coding: utf-8
from __future__ import unicode_literals

import pytest


# Note: "chromosomes" worked previous the bug fix
@pytest.mark.parametrize('word,lemma', [("chromosomes", "chromosome"), ("endosomes", "endosome"), ("colocalizes", "colocalize")])
def test_issue781(path, lemmatizer, word, lemma):
    assert lemmatizer(word, 'noun', morphology={'number': 'plur'}) == set([lemma])

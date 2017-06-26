# coding: utf-8
from __future__ import unicode_literals

import pytest


# Note: "chromosomes" worked previous the bug fix
@pytest.mark.models('en')
@pytest.mark.parametrize('word,lemmas', [("chromosomes", ["chromosome"]), ("endosomes", ["endosome"]), ("colocalizes", ["colocalize", "colocaliz"])])
def test_issue781(EN, word, lemmas):
    lemmatizer = EN.Defaults.create_lemmatizer()
    assert lemmatizer(word, 'noun', morphology={'number': 'plur'}) == set(lemmas)

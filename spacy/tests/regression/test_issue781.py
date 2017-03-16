# coding: utf-8
from __future__ import unicode_literals

import pytest


# Note: "chromosomes" worked previous the bug fix
@pytest.mark.parametrize('word,lemmas', [("chromosomes", ["chromosome"]), ("endosomes", ["endosome"]), ("colocalizes", ["colocalize", "colocaliz"])])
def test_issue781(lemmatizer, word, lemmas):
    assert lemmatizer(word, 'noun', morphology={'number': 'plur'}) == set(lemmas)

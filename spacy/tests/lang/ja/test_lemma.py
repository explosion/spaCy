# coding: utf-8
from __future__ import unicode_literals

import pytest

LEMMAS = (
        ('新しく', '新しい'),
        ('赤く', '赤い'),
        ('すごく', '凄い'),
        ('いただきました', '頂く'),
        ('なった', '成る'))

@pytest.mark.parametrize('word,lemma', LEMMAS)
def test_japanese_lemmas(JA, word, lemma):
    test_lemma = JA(word)[0].lemma_
    assert test_lemma == lemma



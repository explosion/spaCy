# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize(
    "word,lemma",
    [("新しく", "新しい"), ("赤く", "赤い"), ("すごく", "凄い"), ("いただきました", "頂く"), ("なった", "成る")],
)
def test_ja_lemmatizer_assigns(ja_tokenizer, word, lemma):
    test_lemma = ja_tokenizer(word)[0].lemma_
    assert test_lemma == lemma

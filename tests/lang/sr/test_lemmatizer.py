# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize(
    "string,lemma",
    [
        ("најадекватнији", "адекватан"),
        ("матурирао", "матурирати"),
        ("планираћемо", "планирати"),
        ("певају", "певати"),
        ("нама", "ми"),
        ("се", "себе"),
    ],
)
def test_sr_lemmatizer_lookup_assigns(sr_tokenizer, string, lemma):
    tokens = sr_tokenizer(string)
    assert tokens[0].lemma_ == lemma

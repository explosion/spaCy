# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize(
    "string,lemma",
    [
        ("Dëscher", "Dësch"),
        ("engagéiers", "engagéieren"),
        ("goung", "goen"),
        ("neit", "nei"),
        ("déi", "déi"),
        ("Männer", "Mann"),
        ("Mënner", "Mond"),
        ("kritt", "kréien")
    ],
)
def test_lb_lemmatizer_lookup_assigns(lb_tokenizer, string, lemma):
    tokens = lb_tokenizer(string)
    assert tokens[0].lemma_ == lemma

# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize(
    "string,lemma",
    [
        ("DNA-profilernas", "DNA-profil"),
        ("Elfenbenskustens", "Elfenbenskusten"),
        ("abortmotståndarens", "abortmotståndare"),
        ("kolesterols", "kolesterol"),
        ("portionssnusernas", "portionssnus"),
        ("åsyns", "åsyn"),
    ],
)
def test_lemmatizer_lookup_assigns(sv_tokenizer, string, lemma):
    tokens = sv_tokenizer(string)
    assert tokens[0].lemma_ == lemma

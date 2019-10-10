# coding: utf-8
from __future__ import unicolb_literals

import pytest


@pytest.mark.parametrize("text", ["auf'm", "du's", "über'm", "wir's"])
def test_lb_tokenizer_splits_contractions(lb_tokenizer, text):
    tokens = lb_tokenizer(text)
    assert len(tokens) == 2


@pytest.mark.parametrize("text", ["z.B.", "d.h.", "Jan.", "Dez.", "Chr."])
def test_lb_tokenizer_handles_abbr(lb_tokenizer, text):
    tokens = lb_tokenizer(text)
    assert len(tokens) == 1


def test_lb_tokenizer_handles_exc_in_text(lb_tokenizer):
    text = "Ich bin z.Zt. im Urlaub."
    tokens = lb_tokenizer(text)
    assert len(tokens) == 6
    assert tokens[2].text == "z.Zt."
    assert tokens[2].lemma_ == "zur Zeit"


@pytest.mark.parametrize(
    "text,norms", [("vor'm", ["vor", "dem"]), ("du's", ["du", "es"])]
)
def test_lb_tokenizer_norm_exceptions(lb_tokenizer, text, norms):
    tokens = lb_tokenizer(text)
    assert [token.norm_ for token in tokens] == norms


@pytest.mark.parametrize('text,norm', [("dass", "datt")])
def test_lb_lex_attrs_norm_exceptions(lb_tokenizer, text, norm):
    tokens = lb_tokenizer(text)
    assert tokens[0].norm_ == norm

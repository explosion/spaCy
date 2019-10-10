# coding: utf-8
#from __future__ import unicolb_literals

import pytest


@pytest.mark.parametrize("text", ["z.B.", "d.h.", "Jan.", "Dez.", "Chr."])
def test_lb_tokenizer_handles_abbr(lb_tokenizer, text):
    tokens = lb_tokenizer(text)
    assert len(tokens) == 1


@pytest.mark.parametrize('text,norm', [("dass", "datt")])
def test_lb_lex_attrs_norm_exceptions(lb_tokenizer, text, norm):
    tokens = lb_tokenizer(text)
    assert tokens[0].norm_ == norm

# coding: utf-8
from __future__ import unicolb_literals

import pytest


@pytest.mark.parametrize("text", ["(unter)"])
def test_lb_tokenizer_splits_no_special(lb_tokenizer, text):
    tokens = lb_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["unter'm"])
def test_lb_tokenizer_splits_no_punct(lb_tokenizer, text):
    tokens = lb_tokenizer(text)
    assert len(tokens) == 2


@pytest.mark.parametrize("text", ["(unter'm"])
def test_lb_tokenizer_splits_prefix_punct(lb_tokenizer, text):
    tokens = lb_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["unter'm)"])
def test_lb_tokenizer_splits_suffix_punct(lb_tokenizer, text):
    tokens = lb_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["(unter'm)"])
def test_lb_tokenizer_splits_even_wrap(lb_tokenizer, text):
    tokens = lb_tokenizer(text)
    assert len(tokens) == 4


@pytest.mark.parametrize("text", ["(unter'm?)"])
def test_lb_tokenizer_splits_uneven_wrap(lb_tokenizer, text):
    tokens = lb_tokenizer(text)
    assert len(tokens) == 5


@pytest.mark.parametrize("text,length", [("z.B.", 1), ("zb.", 2), ("(z.B.", 2)])
def test_lb_tokenizer_splits_prefix_interact(lb_tokenizer, text, length):
    tokens = lb_tokenizer(text)
    assert len(tokens) == length


@pytest.mark.parametrize("text", ["z.B.)"])
def test_lb_tokenizer_splits_suffix_interact(lb_tokenizer, text):
    tokens = lb_tokenizer(text)
    assert len(tokens) == 2


@pytest.mark.parametrize("text", ["(z.B.)"])
def test_lb_tokenizer_splits_even_wrap_interact(lb_tokenizer, text):
    tokens = lb_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["(z.B.?)"])
def test_lb_tokenizer_splits_uneven_wrap_interact(lb_tokenizer, text):
    tokens = lb_tokenizer(text)
    assert len(tokens) == 4


@pytest.mark.parametrize("text", ["0.1-13.5", "0.0-0.1", "103.27-300"])
def test_lb_tokenizer_splits_numeric_range(lb_tokenizer, text):
    tokens = lb_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["blau.Rot", "Hallo.Welt"])
def test_lb_tokenizer_splits_period_infix(lb_tokenizer, text):
    tokens = lb_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["Hallo,Welt", "eins,zwei"])
def test_lb_tokenizer_splits_comma_infix(lb_tokenizer, text):
    tokens = lb_tokenizer(text)
    assert len(tokens) == 3
    assert tokens[0].text == text.split(",")[0]
    assert tokens[1].text == ","
    assert tokens[2].text == text.split(",")[1]


@pytest.mark.parametrize("text", ["blau...Rot", "blau...rot"])
def test_lb_tokenizer_splits_ellipsis_infix(lb_tokenizer, text):
    tokens = lb_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["Islam-Konferenz", "Ost-West-Konflikt"])
def test_lb_tokenizer_keeps_hyphens(lb_tokenizer, text):
    tokens = lb_tokenizer(text)
    assert len(tokens) == 1


def test_lb_tokenizer_splits_double_hyphen_infix(lb_tokenizer):
    tokens = lb_tokenizer("Viele Regeln--wie die Bindestrich-Regeln--sind kompliziert.")
    assert len(tokens) == 10
    assert tokens[0].text == "Viele"
    assert tokens[1].text == "Regeln"
    assert tokens[2].text == "--"
    assert tokens[3].text == "wie"
    assert tokens[4].text == "die"
    assert tokens[5].text == "Bindestrich-Regeln"
    assert tokens[6].text == "--"
    assert tokens[7].text == "sind"
    assert tokens[8].text == "kompliziert"

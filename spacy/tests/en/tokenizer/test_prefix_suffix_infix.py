# coding: utf-8
"""Test that tokenizer prefixes, suffixes and infixes are handled correctly."""


from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize('text', ["(can)"])
def test_tokenizer_splits_no_special(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize('text', ["can't"])
def test_tokenizer_splits_no_punct(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 2


@pytest.mark.parametrize('text', ["(can't"])
def test_tokenizer_splits_prefix_punct(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize('text', ["can't)"])
def test_tokenizer_splits_suffix_punct(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize('text', ["(can't)"])
def test_tokenizer_splits_even_wrap(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 4


@pytest.mark.parametrize('text', ["(can't?)"])
def test_tokenizer_splits_uneven_wrap(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 5


@pytest.mark.parametrize('text,length', [("U.S.", 1), ("us.", 2), ("(U.S.", 2)])
def test_tokenizer_splits_prefix_interact(en_tokenizer, text, length):
    tokens = en_tokenizer(text)
    assert len(tokens) == length


@pytest.mark.parametrize('text', ["U.S.)"])
def test_tokenizer_splits_suffix_interact(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 2


@pytest.mark.parametrize('text', ["(U.S.)"])
def test_tokenizer_splits_even_wrap_interact(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize('text', ["(U.S.?)"])
def test_tokenizer_splits_uneven_wrap_interact(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 4


@pytest.mark.parametrize('text', ["best-known"])
def test_tokenizer_splits_hyphens(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize('text', ["0.1-13.5", "0.0-0.1", "103.27-300"])
def test_tokenizer_splits_numeric_range(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize('text', ["best.Known", "Hello.World"])
def test_tokenizer_splits_period_infix(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize('text', ["Hello,world", "one,two"])
def test_tokenizer_splits_comma_infix(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 3
    assert tokens[0].text == text.split(",")[0]
    assert tokens[1].text == ","
    assert tokens[2].text == text.split(",")[1]


@pytest.mark.parametrize('text', ["best...Known", "best...known"])
def test_tokenizer_splits_ellipsis_infix(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 3


def test_tokenizer_splits_double_hyphen_infix(en_tokenizer):
    tokens = en_tokenizer("No decent--let alone well-bred--people.")
    assert tokens[0].text == "No"
    assert tokens[1].text == "decent"
    assert tokens[2].text == "--"
    assert tokens[3].text == "let"
    assert tokens[4].text == "alone"
    assert tokens[5].text == "well"
    assert tokens[6].text == "-"
    assert tokens[7].text == "bred"
    assert tokens[8].text == "--"
    assert tokens[9].text == "people"


@pytest.mark.xfail
def test_tokenizer_splits_period_abbr(en_tokenizer):
    text = "Today is Tuesday.Mr."
    tokens = en_tokenizer(text)
    assert len(tokens) == 5
    assert tokens[0].text == "Today"
    assert tokens[1].text == "is"
    assert tokens[2].text == "Tuesday"
    assert tokens[3].text == "."
    assert tokens[4].text == "Mr."


@pytest.mark.xfail
def test_tokenizer_splits_em_dash_infix(en_tokenizer):
    # Re Issue #225
    tokens = en_tokenizer("""Will this road take me to Puddleton?\u2014No, """
                          """you'll have to walk there.\u2014Ariel.""")
    assert tokens[6].text == "Puddleton"
    assert tokens[7].text == "?"
    assert tokens[8].text == "\u2014"

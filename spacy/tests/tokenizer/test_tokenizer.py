# coding: utf-8
from __future__ import unicode_literals

import pytest


def test_tokenizer_handles_no_word(tokenizer):
    tokens = tokenizer("")
    assert len(tokens) == 0


@pytest.mark.parametrize('text', ["lorem"])
def test_tokenizer_handles_single_word(tokenizer, text):
    tokens = tokenizer(text)
    assert tokens[0].text == text


@pytest.mark.parametrize('text', ["lorem ipsum"])
def test_tokenizer_handles_two_words(tokenizer, text):
    tokens = tokenizer(text)
    assert len(tokens) == 2
    assert tokens[0].text != tokens[1].text


@pytest.mark.parametrize('text', ["lorem  ipsum"])
def test_tokenizer_splits_double_space(tokenizer, text):
    tokens = tokenizer(text)
    assert len(tokens) == 3
    assert tokens[1].text == " "


@pytest.mark.parametrize('text', ["lorem\nipsum"])
def test_tokenizer_splits_newline(tokenizer, text):
    tokens = tokenizer(text)
    assert len(tokens) == 3
    assert tokens[1].text == "\n"


def test_tokenizer_handles_punct(tokenizer):
    text = "Lorem, ipsum."
    tokens = tokenizer(text)
    assert len(tokens) == 4
    assert tokens[0].text == "Lorem"
    assert tokens[1].text == ","
    assert tokens[2].text == "ipsum"
    assert tokens[1].text != "Lorem"


def test_tokenizer_handles_digits(tokenizer):
    exceptions = ["hu"]
    text = "Lorem ipsum: 1984."
    tokens = tokenizer(text)

    if tokens[0].lang_ not in exceptions:
        assert len(tokens) == 5
        assert tokens[0].text == "Lorem"
        assert tokens[3].text == "1984"


def test_tokenizer_handles_long_text(tokenizer):
    text = """Lorem ipsum dolor sit amet, consectetur adipiscing elit

Cras egestas orci non porttitor maximus.
Maecenas quis odio id dolor rhoncus dignissim. Curabitur sed velit at orci ultrices sagittis. Nulla commodo euismod arcu eget vulputate.

Phasellus tincidunt, augue quis porta finibus, massa sapien consectetur augue, non lacinia enim nibh eget ipsum. Vestibulum in bibendum mauris.

"Nullam porta fringilla enim, a dictum orci consequat in." Mauris nec malesuada justo."""

    tokens = tokenizer(text)
    assert len(tokens) > 5


def test_tokenizer_suspected_freeing_strings(tokenizer):
    text1 = "Lorem dolor sit amet, consectetur adipiscing elit."
    text2 = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    tokens1 = tokenizer(text1)
    tokens2 = tokenizer(text2)
    assert tokens1[0].text == "Lorem"
    assert tokens2[0].text == "Lorem"

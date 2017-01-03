from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize('text', ["best-known"])
def test_tokenizer_splits_hyphens(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize('text', ["0.1-13.5", "0.0-0.1", "103.27-300"])
def test_tokenizer_splits_numeric_range(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize('text', ["best.Known", "Hello.World"])
def test_tokenizer_splits_period(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize('text', ["Hello,world", "one,two"])
def test_tokenizer_splits_comma(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 3
    assert tokens[0].text == text.split(",")[0]
    assert tokens[1].text == ","
    assert tokens[2].text == text.split(",")[1]


@pytest.mark.parametrize('text', ["best...Known", "best...known"])
def test_tokenizer_splits_ellipsis(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize('text', ["google.com", "python.org", "spacy.io", "explosion.ai"])
def test_tokenizer_keep_urls(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 1


@pytest.mark.parametrize('text', ["hello123@example.com", "hi+there@gmail.it", "matt@explosion.ai"])
def test_tokenizer_keeps_email(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 1


def test_tokenizer_splits_double_hyphen(en_tokenizer):
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

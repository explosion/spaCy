# coding: utf-8
from __future__ import unicode_literals

from ...vocab import Vocab
from ...tokenizer import Tokenizer
from ...util import utf8open

from os import path
import pytest


def test_tokenizer_handles_no_word(tokenizer):
    tokens = tokenizer("")
    assert len(tokens) == 0


@pytest.mark.parametrize('text', ["lorem"])
def test_tokenizer_handles_single_word(tokenizer, text):
    tokens = tokenizer(text)
    assert tokens[0].text == text


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


@pytest.mark.parametrize('text', ["google.com", "python.org", "spacy.io", "explosion.ai"])
def test_tokenizer_keep_urls(tokenizer, text):
    tokens = tokenizer(text)
    assert len(tokens) == 1


@pytest.mark.parametrize('text', ["hello123@example.com", "hi+there@gmail.it", "matt@explosion.ai"])
def test_tokenizer_keeps_email(tokenizer, text):
    tokens = tokenizer(text)
    assert len(tokens) == 1


def test_tokenizer_handles_long_text(tokenizer):
    text = """Lorem ipsum dolor sit amet, consectetur adipiscing elit

Cras egestas orci non porttitor maximus.
Maecenas quis odio id dolor rhoncus dignissim. Curabitur sed velit at orci ultrices sagittis. Nulla commodo euismod arcu eget vulputate.

Phasellus tincidunt, augue quis porta finibus, massa sapien consectetur augue, non lacinia enim nibh eget ipsum. Vestibulum in bibendum mauris.

"Nullam porta fringilla enim, a dictum orci consequat in." Mauris nec malesuada justo."""

    tokens = tokenizer(text)
    assert len(tokens) > 5


@pytest.mark.parametrize('file_name', ["sun.txt"])
def test_tokenizer_handle_text_from_file(tokenizer, file_name):
    loc = path.join(path.dirname(__file__), file_name)
    text = utf8open(loc).read()
    assert len(text) != 0
    tokens = tokenizer(text)
    assert len(tokens) > 100


def test_tokenizer_suspected_freeing_strings(tokenizer):
    text1 = "Lorem dolor sit amet, consectetur adipiscing elit."
    text2 = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    tokens1 = tokenizer(text1)
    tokens2 = tokenizer(text2)
    assert tokens1[0].text == "Lorem"
    assert tokens2[0].text == "Lorem"


@pytest.mark.parametrize('text,tokens', [
    ("lorem", [{'orth': 'lo'}, {'orth': 'rem'}])])
def test_tokenizer_add_special_case(tokenizer, text, tokens):
    tokenizer.add_special_case(text, tokens)
    doc = tokenizer(text)
    assert doc[0].text == tokens[0]['orth']
    assert doc[1].text == tokens[1]['orth']


@pytest.mark.parametrize('text,tokens', [
    ("lorem", [{'orth': 'lo', 'tag': 'NN'}, {'orth': 'rem'}])])
def test_tokenizer_add_special_case_tag(text, tokens):
    vocab = Vocab(tag_map={'NN': {'pos': 'NOUN'}})
    tokenizer = Tokenizer(vocab, {}, None, None, None)
    tokenizer.add_special_case(text, tokens)
    doc = tokenizer(text)
    assert doc[0].text == tokens[0]['orth']
    assert doc[0].tag_ == tokens[0]['tag']
    assert doc[0].pos_ == 'NOUN'
    assert doc[1].text == tokens[1]['orth']

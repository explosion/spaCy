# coding: utf-8
from __future__ import unicode_literals
from os import path

import pytest

from spacy.util import utf8open


def test_tokenizer_handles_no_word(en_tokenizer):
    tokens = en_tokenizer("")
    assert len(tokens) == 0


@pytest.mark.parametrize('text', ["hello"])
def test_tokenizer_handles_single_word(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert tokens[0].text == text


@pytest.mark.parametrize('text', ["hello possums"])
def test_tokenizer_handles_two_words(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 2
    assert tokens[0].text != tokens[1].text


def test_tokenizer_handles_punct(en_tokenizer):
    text = "hello, possums."
    tokens = en_tokenizer(text)
    assert len(tokens) == 4
    assert tokens[0].text == "hello"
    assert tokens[1].text == ","
    assert tokens[2].text == "possums"
    assert tokens[1].text != "hello"


def test_tokenizer_handles_digits(en_tokenizer):
    text = "The year: 1984."
    tokens = en_tokenizer(text)
    assert len(tokens) == 5
    assert tokens[0].text == "The"
    assert tokens[3].text == "1984"


def test_tokenizer_handles_basic_contraction(en_tokenizer):
    text = "don't giggle"
    tokens = en_tokenizer(text)
    assert len(tokens) == 3
    assert tokens[1].text == "n't"
    text = "i said don't!"
    tokens = en_tokenizer(text)
    assert len(tokens) == 5
    assert tokens[4].text == "!"


@pytest.mark.parametrize('text', ["`ain't", '''"isn't''', "can't!"])
def test_tokenizer_handles_basic_contraction_punct(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 3


def test_tokenizer_handles_long_text(en_tokenizer):
    text = """Tributes pour in for late British Labour Party leader

Tributes poured in from around the world Thursday
to the late Labour Party leader John Smith, who died earlier from a massive
heart attack aged 55.

In Washington, the US State Department issued a statement regretting "the
untimely death" of the rapier-tongued Scottish barrister and parliamentarian.

"Mr. Smith, throughout his distinguished"""

    tokens = en_tokenizer(text)
    assert len(tokens) > 5


@pytest.mark.parametrize('file_name', ["sun.txt"])
def test_tokenizer_handle_text_from_file(en_tokenizer, file_name):
    loc = path.join(path.dirname(__file__), file_name)
    text = utf8open(loc).read()
    assert len(text) != 0
    tokens = en_tokenizer(text)
    assert len(tokens) > 100


@pytest.mark.parametrize('text,length', [
    ("The U.S. Army likes Shock and Awe.", 8),
    ("U.N. regulations are not a part of their concern.", 10),
    ("“Isn't it?”", 6),
    ("""Yes! "I'd rather have a walk", Ms. Comble sighed. """, 15),
    ("""'Me too!', Mr. P. Delaware cried. """, 11),
    ("They ran about 10km.", 6),
    # ("But then the 6,000-year ice age came...", 10)
    ])
def test_tokenizer_handles_cnts(en_tokenizer, text, length):
    tokens = en_tokenizer(text)
    assert len(tokens) == length


def test_tokenizer_suspected_freeing_strings(en_tokenizer):
    text1 = "Betty Botter bought a pound of butter."
    text2 = "Betty also bought a pound of butter."
    tokens1 = en_tokenizer(text1)
    tokens2 = en_tokenizer(text2)
    assert tokens1[0].text == "Betty"
    assert tokens2[0].text == "Betty"

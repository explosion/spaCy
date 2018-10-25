# coding: utf-8

from __future__ import unicode_literals

import pytest
from .... import util

@pytest.fixture(scope='module')
def fr_tokenizer():
    return util.get_lang_class('fr').Defaults.create_tokenizer()


@pytest.mark.parametrize('text', ["aujourd'hui", "Aujourd'hui", "prud'hommes",
                                  "prud’hommal"])
def test_tokenizer_infix_exceptions(fr_tokenizer, text):
    tokens = fr_tokenizer(text)
    assert len(tokens) == 1


@pytest.mark.parametrize('text,lemma', [("janv.", "janvier"),
                                        ("juill.", "juillet"),
                                        ("Dr.", "docteur"),
                                        ("av.", "avant"),
                                        ("sept.", "septembre")])
def test_tokenizer_handles_abbr(fr_tokenizer, text, lemma):
    tokens = fr_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].lemma_ == lemma


def test_tokenizer_handles_exc_in_text(fr_tokenizer):
    text = "Je suis allé au mois de janv. aux prud’hommes."
    tokens = fr_tokenizer(text)
    assert len(tokens) == 10
    assert tokens[6].text == "janv."
    assert tokens[6].lemma_ == "janvier"
    assert tokens[8].text == "prud’hommes"


def test_tokenizer_handles_exc_in_text_2(fr_tokenizer):
    text = "Cette après-midi, je suis allé dans un restaurant italo-mexicain."
    tokens = fr_tokenizer(text)
    assert len(tokens) == 11
    assert tokens[1].text == "après-midi"
    assert tokens[9].text == "italo-mexicain"

def test_tokenizer_handles_title(fr_tokenizer):
    text = "N'est-ce pas génial?"
    tokens = fr_tokenizer(text)
    assert len(tokens) == 6
    assert tokens[0].text == "N'"
    assert tokens[0].lemma_ == "ne"
    assert tokens[1].text == "est"
    assert tokens[1].lemma_ == "être"
    assert tokens[2].text == "-ce"
    assert tokens[2].lemma_ == "ce"

def test_tokenizer_handles_title_2(fr_tokenizer):
    text = "Est-ce pas génial?"
    tokens = fr_tokenizer(text)
    assert len(tokens) == 6
    assert tokens[0].text == "Est"
    assert tokens[0].lemma_ == "être"

def test_tokenizer_handles_title_2(fr_tokenizer):
    text = "Qu'est-ce que tu fais?"
    tokens = fr_tokenizer(text)
    assert len(tokens) == 7
    assert tokens[0].text == "Qu'"
    assert tokens[0].lemma_ == "que"

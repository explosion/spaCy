# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.fixture
def i_has(en_tokenizer):
    doc = en_tokenizer("I has")
    doc[0].tag_ = "PRP"
    doc[1].tag_ = "VBZ"
    return doc


def test_token_morph_id(i_has):
    assert i_has[0].morph.id
    assert i_has[1].morph.id != 0
    assert i_has[0].morph.id != i_has[1].morph.id


def test_morph_props(i_has):
    assert i_has[0].morph.pron_type == i_has.vocab.strings["PronType_prs"]
    assert i_has[0].morph.pron_type_ == "PronType_prs"
    assert i_has[1].morph.pron_type == 0


def test_morph_iter(i_has):
    assert list(i_has[0].morph) == ["PronType_prs"]
    assert list(i_has[1].morph) == ["Number_sing", "Person_three", "VerbForm_fin"]


def test_morph_get(i_has):
    assert i_has[0].morph.get("pron_type") == "PronType_prs"

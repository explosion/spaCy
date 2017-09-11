# coding: utf8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize('text', [
    "She hasn't done the housework.",
    "I haven't done it before.",
    "you daren't do that"])
def test_issue1281(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert tokens[2].text == "n't"

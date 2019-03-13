# coding: utf-8
from __future__ import unicode_literals

import pytest


# @pytest.mark.parametrize('text', ["e.g.", "p.m.", "Jan.", "Dec.", "Inc."])
# def test_nl_tokenizer_handles_abbr(nl_tokenizer, text):
#     tokens = nl_tokenizer(text)
#     assert len(tokens) == 1
#
#
# def test_nl_tokenizer_handles_exc_in_text(nl_tokenizer):
#     text = "It's mediocre i.e. bad."
#     tokens = nl_tokenizer(text)
#     assert len(tokens) == 6
#     assert tokens[3].text == "i.e."

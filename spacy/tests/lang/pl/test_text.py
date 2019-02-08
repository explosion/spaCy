# coding: utf-8
"""Words like numbers are recognized correctly."""


from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize('text,match', [
    ('10', True), ('1', True), ('10,000', True), ('10,00', True),
    ('jeden', True), ('dwa', True), ('milion', True),
    ('pies', False), (',', False), ('1/2', True)])
def test_lex_attrs_like_number(pl_tokenizer, text, match):
    tokens = pl_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].like_num == match

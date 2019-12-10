# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize("text", ["z.B.", "Jan."])
def test_lb_tokenizer_handles_abbr(lb_tokenizer, text):
    tokens = lb_tokenizer(text)
    assert len(tokens) == 1

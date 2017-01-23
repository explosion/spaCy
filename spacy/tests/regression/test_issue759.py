# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize('text,is_num', [("one", True), ("ten", True),
                                         ("teneleven", False)])
def test_issue759(en_tokenizer, text, is_num):
    """Test that numbers are recognised correctly."""
    tokens = en_tokenizer(text)
    assert tokens[0].like_num == is_num

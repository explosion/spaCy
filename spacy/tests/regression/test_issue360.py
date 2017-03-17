# coding: utf-8
from __future__ import unicode_literals

import pytest


def test_issue360(en_tokenizer):
    """Test tokenization of big ellipsis"""
    tokens = en_tokenizer('$45...............Asking')
    assert len(tokens) > 2

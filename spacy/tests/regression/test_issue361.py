# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize('text1,text2', [("cat", "dog")])
def test_issue361(en_vocab, text1, text2):
    """Test Issue #361: Equality of lexemes"""
    assert en_vocab[text1] == en_vocab[text1]
    assert en_vocab[text1] != en_vocab[text2]

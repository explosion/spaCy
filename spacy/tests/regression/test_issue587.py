# coding: utf-8
from __future__ import unicode_literals

from ...matcher import Matcher
from ...attrs import IS_PUNCT, ORTH

import pytest


def test_issue587(en_tokenizer):
    """Test that Matcher doesn't segfault on particular input"""
    doc = en_tokenizer('a b; c')
    matcher = Matcher(doc.vocab)
    matcher.add('TEST1', None, [{ORTH: 'a'}, {ORTH: 'b'}])
    matches = matcher(doc)
    assert len(matches) == 1
    matcher.add('TEST2', None, [{ORTH: 'a'}, {ORTH: 'b'}, {IS_PUNCT: True}, {ORTH: 'c'}])
    matches = matcher(doc)
    assert len(matches) == 2
    matcher.add('TEST3', None, [{ORTH: 'a'}, {ORTH: 'b'}, {IS_PUNCT: True}, {ORTH: 'd'}])
    matches = matcher(doc)
    assert len(matches) == 2

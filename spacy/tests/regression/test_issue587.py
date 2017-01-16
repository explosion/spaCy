# coding: utf-8
from __future__ import unicode_literals

from ...matcher import Matcher
from ...attrs import IS_PUNCT, ORTH

import pytest


@pytest.mark.models
def test_issue587(EN):
    """Test that Matcher doesn't segfault on particular input"""
    matcher = Matcher(EN.vocab)
    content = '''a b; c'''
    matcher.add(entity_key='1', label='TEST', attrs={}, specs=[[{ORTH: 'a'}, {ORTH: 'b'}]])
    matcher(EN(content))
    matcher.add(entity_key='2', label='TEST', attrs={}, specs=[[{ORTH: 'a'}, {ORTH: 'b'}, {IS_PUNCT: True}, {ORTH: 'c'}]])
    matcher(EN(content))
    matcher.add(entity_key='3', label='TEST', attrs={}, specs=[[{ORTH: 'a'}, {ORTH: 'b'}, {IS_PUNCT: True}, {ORTH: 'd'}]])
    matcher(EN(content))

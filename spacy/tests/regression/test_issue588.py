# coding: utf-8
from __future__ import unicode_literals

from ...matcher import Matcher

import pytest


def test_issue588(en_vocab):
    matcher = Matcher(en_vocab)
    with pytest.raises(ValueError):
        matcher.add(entity_key='1', label='TEST', attrs={}, specs=[[]])

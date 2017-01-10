# coding: utf-8
from __future__ import unicode_literals

from ...vocab import Vocab
from ...tokens import Doc
from ...matcher import Matcher

import pytest


def test_issue588():
    matcher = Matcher(Vocab())
    with pytest.raises(ValueError):
        matcher.add(entity_key='1', label='TEST', attrs={}, specs=[[]])

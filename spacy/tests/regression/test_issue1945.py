'''Test regression in Matcher introduced in v2.0.6.'''
from __future__ import unicode_literals
import pytest

from ...vocab import Vocab
from ...tokens import Doc
from ...matcher import Matcher

@pytest.mark.xfail
def test_issue1945():
    text = "a a a"
    matcher = Matcher(Vocab())
    matcher.add('MWE', None, [{'orth': 'a'}, {'orth': 'a'}])
    doc = Doc(matcher.vocab, words=['a', 'a', 'a'])
    matches = matcher(doc)
    # We should see two overlapping matches here
    assert len(matches) == 2
    assert matches[0][1:] == (0, 2)
    assert matches[1][1:] == (1, 3)

'''
Test Matcher matches with '*' operator and Boolean flag
'''
from __future__ import unicode_literals
import pytest

from ...matcher import Matcher
from ...vocab import Vocab
from ...attrs import LOWER
from ...tokens import Doc


@pytest.mark.xfail
def test_issue850():
    matcher = Matcher(Vocab())
    IS_ANY_TOKEN = matcher.vocab.add_flag(lambda x: True)
    matcher.add_pattern(
        "FarAway",
        [
            {LOWER: "bob"},
            {'OP': '*', IS_ANY_TOKEN: True},
            {LOWER: 'frank'}
        ])
    doc = Doc(matcher.vocab, words=['bob', 'and', 'and', 'cat', 'frank'])
    match = matcher(doc)
    assert len(match) == 1
    start, end, label, ent_id = match 
    assert start == 0
    assert end == 4

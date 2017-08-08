# coding: utf-8
from __future__ import unicode_literals

from ...matcher import Matcher

import pytest


def test_issue242(en_tokenizer):
    """Test overlapping multi-word phrases."""
    text = "There are different food safety standards in different countries."
    patterns = [[{'LOWER': 'food'}, {'LOWER': 'safety'}],
                [{'LOWER': 'safety'}, {'LOWER': 'standards'}]]

    doc = en_tokenizer(text)
    matcher = Matcher(doc.vocab)
    matcher.add('FOOD', None, *patterns)

    matches = [(ent_type, start, end) for ent_type, start, end in matcher(doc)]
    doc.ents += tuple(matches)
    match1, match2 = matches
    assert match1[1] == 3
    assert match1[2] == 5
    assert match2[1] == 4
    assert match2[2] == 6

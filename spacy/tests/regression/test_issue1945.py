'''Test regression in PhraseMatcher introduced in v2.0.6.'''
from __future__ import unicode_literals
import pytest

from ...lang.en import English
from ...matcher import PhraseMatcher

@pytest.mark.xfail
def test_issue1945():
    text = "deep machine learning"
    mw_list = ["machine learning", "deep blue", "planing machine"]

    nlp = English()
    matcher = PhraseMatcher(nlp.vocab)
    matcher.add("MWE", None, *[nlp.tokenizer(item) for item in mw_list])

    assert len(matcher(nlp(text))) == 1

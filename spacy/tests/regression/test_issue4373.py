# coding: utf8
from __future__ import unicode_literals

from spacy.matcher import Matcher, PhraseMatcher
from spacy.vocab import Vocab


def test_issue4373():
    """Test that PhraseMatcher.vocab can be accessed (like Matcher.vocab)."""
    matcher = Matcher(Vocab())
    assert isinstance(matcher.vocab, Vocab)
    matcher = PhraseMatcher(Vocab())
    assert isinstance(matcher.vocab, Vocab)

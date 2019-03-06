# coding: utf-8
from __future__ import unicode_literals

from spacy.matcher import Matcher
from spacy.tokens import Doc


def test_issue3328(en_vocab):
    doc = Doc(en_vocab, words=["Hello", ",", "how", "are", "you", "doing", "?"])
    matcher = Matcher(en_vocab)
    patterns = [
        [{"LOWER": {"IN": ["hello", "how"]}}],
        [{"LOWER": {"IN": ["you", "doing"]}}],
    ]
    matcher.add("TEST", None, *patterns)
    matches = matcher(doc)
    assert len(matches) == 4
    matched_texts = [doc[start:end].text for _, start, end in matches]
    assert matched_texts == ["Hello", "how", "you", "doing"]

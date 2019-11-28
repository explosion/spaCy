# coding: utf-8
from __future__ import unicode_literals

from mock import Mock
from spacy.matcher import DependencyMatcher
from ..util import get_doc


def test_issue4590(en_vocab):
    """Test that matches param in on_match method are the same as matches run with no on_match method"""
    pattern = [
        {"SPEC": {"NODE_NAME": "jumped"}, "PATTERN": {"ORTH": "jumped"}},
        {
            "SPEC": {"NODE_NAME": "fox", "NBOR_RELOP": ">", "NBOR_NAME": "jumped"},
            "PATTERN": {"ORTH": "fox"},
        },
        {
            "SPEC": {"NODE_NAME": "quick", "NBOR_RELOP": ".", "NBOR_NAME": "jumped"},
            "PATTERN": {"ORTH": "fox"},
        },
    ]

    on_match = Mock()

    matcher = DependencyMatcher(en_vocab)
    matcher.add("pattern", on_match, pattern)

    text = "The quick brown fox jumped over the lazy fox"
    heads = [3, 2, 1, 1, 0, -1, 2, 1, -3]
    deps = ["det", "amod", "amod", "nsubj", "prep", "pobj", "det", "amod"]

    doc = get_doc(en_vocab, text.split(), heads=heads, deps=deps)

    matches = matcher(doc)

    on_match_args = on_match.call_args

    assert on_match_args[0][3] == matches

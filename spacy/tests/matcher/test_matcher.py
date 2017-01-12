# coding: utf-8
from __future__ import unicode_literals

from ...matcher import Matcher
from ..util import get_doc

import pytest


@pytest.mark.parametrize('words', [["Some", "words"]])
def test_matcher_init(en_vocab, words):
    matcher = Matcher(en_vocab)
    doc = get_doc(en_vocab, words)
    assert matcher.n_patterns == 0
    assert matcher(doc) == []

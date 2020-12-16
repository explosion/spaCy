# coding: utf8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize("word", ["don't", "don’t", "I'd", "I’d"])
def test_issue3521(en_tokenizer, word):
    tok = en_tokenizer(word)[1]
    # 'not' and 'would' should be stopwords, also in their abbreviated forms
    assert tok.is_stop

# coding: utf8
import pytest


@pytest.mark.parametrize(
    "word",
    [
        u"don't",
        u"don’t",
        u"I'd",
        u"I’d",
    ],
)
def test_issue3521(en_tokenizer, word):
    tok = en_tokenizer(word)[1]
    # 'not' and 'would' should be stopwords, also in their abbreviated forms
    assert tok.is_stop

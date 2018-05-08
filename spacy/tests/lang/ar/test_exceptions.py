# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize('text',
                         ["ق.م", "إلخ", "ص.ب", "ت."])
def test_ar_tokenizer_handles_abbr(ar_tokenizer, text):
    tokens = ar_tokenizer(text)
    assert len(tokens) == 1


def test_ar_tokenizer_handles_exc_in_text(ar_tokenizer):
    text = u"تعود الكتابة الهيروغليفية إلى سنة 3200 ق.م"
    tokens = ar_tokenizer(text)
    assert len(tokens) == 7
    assert tokens[6].text == "ق.م"
    assert tokens[6].lemma_ == "قبل الميلاد"


def test_ar_tokenizer_handles_exc_in_text(ar_tokenizer):
    text = u"يبلغ طول مضيق طارق 14كم "
    tokens = ar_tokenizer(text)
    print([(tokens[i].text, tokens[i].suffix_) for i in range(len(tokens))])
    assert len(tokens) == 6

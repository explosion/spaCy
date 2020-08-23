# coding: utf-8
from __future__ import unicode_literals

import pytest


def test_sa_tokenizer_handles_long_text(sa_tokenizer):
    text = """नानाविधानि दिव्यानि नानावर्णाकृतीनि च।।"""
    tokens = sa_tokenizer(text)
    assert len(tokens) == 6


@pytest.mark.parametrize(
    "text,length",
    [
        ("श्री भगवानुवाच पश्य मे पार्थ रूपाणि शतशोऽथ सहस्रशः।", 9,),
        ("गुणान् सर्वान् स्वभावो मूर्ध्नि वर्तते ।", 6),
    ],
)
def test_sa_tokenizer_handles_cnts(sa_tokenizer, text, length):
    tokens = sa_tokenizer(text)
    assert len(tokens) == length

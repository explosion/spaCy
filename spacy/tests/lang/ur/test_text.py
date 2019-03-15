# coding: utf-8
from __future__ import unicode_literals

import pytest


def test_ur_tokenizer_handles_long_text(ur_tokenizer):
    text = """اصل میں رسوا ہونے کی ہمیں
     کچھ عادت سی ہو گئی ہے اس لئے جگ ہنسائی کا ذکر نہیں کرتا،ہوا کچھ یوں کہ عرصہ چھ سال بعد ہمیں بھی خیال آیا
     کہ ایک عدد ٹیلی ویژن ہی کیوں نہ خرید لیں ، سوچا ورلڈ کپ ہی دیکھیں گے۔اپنے پاکستان کے کھلاڑیوں کو دیکھ کر
    ورلڈ کپ دیکھنے کا حوصلہ ہی نہ رہا تو اب یوں ہی ادھر اُدھر کے چینل گھمانے لگ پڑتے ہیں۔"""
    tokens = ur_tokenizer(text)
    assert len(tokens) == 78


@pytest.mark.parametrize("text,length", [("تحریر باسط حبیب", 3), ("میرا پاکستان", 2)])
def test_ur_tokenizer_handles_cnts(ur_tokenizer, text, length):
    tokens = ur_tokenizer(text)
    assert len(tokens) == length

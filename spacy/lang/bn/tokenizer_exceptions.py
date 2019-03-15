# coding=utf-8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA


_exc = {}


for exc_data in [
    {ORTH: "ডঃ", LEMMA: "ডক্টর"},
    {ORTH: "ডাঃ", LEMMA: "ডাক্তার"},
    {ORTH: "ড.", LEMMA: "ডক্টর"},
    {ORTH: "ডা.", LEMMA: "ডাক্তার"},
    {ORTH: "মোঃ", LEMMA: "মোহাম্মদ"},
    {ORTH: "মো.", LEMMA: "মোহাম্মদ"},
    {ORTH: "সে.", LEMMA: "সেলসিয়াস"},
    {ORTH: "কি.মি.", LEMMA: "কিলোমিটার"},
    {ORTH: "কি.মি", LEMMA: "কিলোমিটার"},
    {ORTH: "সে.মি.", LEMMA: "সেন্টিমিটার"},
    {ORTH: "সে.মি", LEMMA: "সেন্টিমিটার"},
    {ORTH: "মি.লি.", LEMMA: "মিলিলিটার"},
]:
    _exc[exc_data[ORTH]] = [exc_data]


TOKENIZER_EXCEPTIONS = _exc

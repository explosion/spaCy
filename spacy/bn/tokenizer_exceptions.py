# coding=utf-8
from __future__ import unicode_literals

from ..symbols import *

TOKENIZER_EXCEPTIONS = {}

ABBREVIATIONS = {
    "ডঃ": [
        {ORTH: "ডঃ", LEMMA: "ডক্টর"},
    ],
    "ডাঃ": [
        {ORTH: "ডাঃ", LEMMA: "ডাক্তার"},
    ],
    "ড.": [
        {ORTH: "ড.", LEMMA: "ডক্টর"},
    ],
    "ডা.": [
        {ORTH: "ডা.", LEMMA: "ডাক্তার"},
    ],
    "মোঃ": [
        {ORTH: "মোঃ", LEMMA: "মোহাম্মদ"},
    ],
    "মো.": [
        {ORTH: "মো.", LEMMA: "মোহাম্মদ"},
    ],
    "সে.": [
        {ORTH: "সে.", LEMMA: "সেলসিয়াস"},
    ],
    "কি.মি": [
        {ORTH: "কি.মি", LEMMA: "কিলোমিটার"},
        {ORTH: "কি.মি.", LEMMA: "কিলোমিটার"},
    ],
    "সে.মি": [
        {ORTH: "সে.মি", LEMMA: "সেন্টিমিটার"},
        {ORTH: "সে.মি.", LEMMA: "সেন্টিমিটার"},
    ],
}

TOKENIZER_EXCEPTIONS.update(ABBREVIATIONS)

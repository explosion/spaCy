# coding: utf8
from __future__ import unicode_literals

from ..norm_exceptions import BASE_NORMS
from ...attrs import NORM, LIKE_NUM


# fmt: off
_stem_suffixes = [
    ["ा", "ि", "ी", "ु", "ू", "ृ", "े", "ै", "ो", "ौ"],
    ["ँ", "ं", "्", "ः"],
    ["लाई", "ले", "बाट", "को", "मा", "हरू"],
    ["हरूलाई", "हरूले", "हरूबाट", "हरूको", "हरूमा"],
    ["इलो", "िलो", "नु", "ाउनु", "ई", "इन", "इन्", "इनन्"],
    ["एँ", "इँन्", "इस्", "इनस्", "यो", "एन", "यौं", "एनौं", "ए", "एनन्"],
    ["छु", "छौँ", "छस्", "छौ", "छ", "छन्", "छेस्", "छे", "छ्यौ", "छिन्", "हुन्छ"],
    ["दै", "दिन", "दिँन", "दैनस्", "दैन", "दैनौँ", "दैनौं", "दैनन्"],
    ["हुन्न", "न्न", "न्न्स्", "न्नौं", "न्नौ", "न्न्न्", "िई"],
    ["अ", "ओ", "ऊ", "अरी", "साथ", "वित्तिकै", "पूर्वक"],
    ["याइ", "ाइ", "बार", "वार", "चाँहि"],
    ["ने", "ेको", "ेकी", "ेका", "ेर", "दै", "तै", "िकन", "उ", "न", "नन्"]
]
# fmt: on

# reference 1: https://en.wikipedia.org/wiki/Numbers_in_Nepali_language
# reference 2: https://www.imnepal.com/nepali-numbers/
_num_words = [
    "शुन्य",
    "एक",
    "दुई",
    "तीन",
    "चार",
    "पाँच",
    "छ",
    "सात",
    "आठ",
    "नौ",
    "दश",
    "एघार",
    "बाह्र",
    "तेह्र",
    "चौध",
    "पन्ध्र",
    "सोह्र",
    "सोह्र",
    "सत्र",
    "अठार",
    "उन्नाइस",
    "बीस",
    "तीस",
    "चालीस",
    "पचास",
    "साठी",
    "सत्तरी",
    "असी",
    "नब्बे",
    "सय",
    "हजार",
    "लाख",
    "करोड",
    "अर्ब",
    "खर्ब",
]


def norm(string):
    # normalise base exceptions,  e.g. punctuation or currency symbols
    if string in BASE_NORMS:
        return BASE_NORMS[string]
    # set stem word as norm,  if available,  adapted from:
    # https://github.com/explosion/spaCy/blob/master/spacy/lang/hi/lex_attrs.py
    # https://www.researchgate.net/publication/237261579_Structure_of_Nepali_Grammar
    for suffix_group in reversed(_stem_suffixes):
        length = len(suffix_group[0])
        if len(string) <= length:
            break
        for suffix in suffix_group:
            if string.endswith(suffix):
                return string[:-length]
    return string


def like_num(text):
    if text.startswith(("+", "-", "±", "~")):
        text = text[1:]
    text = text.replace(", ", "").replace(".", "")
    if text.isdigit():
        return True
    if text.count("/") == 1:
        num, denom = text.split("/")
        if num.isdigit() and denom.isdigit():
            return True
    if text.lower() in _num_words:
        return True
    return False


LEX_ATTRS = {NORM: norm, LIKE_NUM: like_num}

# coding: utf8
from __future__ import unicode_literals

from ..norm_exceptions import BASE_NORMS
from ...attrs import NORM
from ...attrs import LIKE_NUM
from ...util import add_lookups


_stem_suffixes = [
    ["ो", "े", "ू", "ु", "ी", "ि", "ा"],
    ["कर", "ाओ", "िए", "ाई", "ाए", "ने", "नी", "ना", "ते", "ीं", "ती", "ता", "ाँ", "ां", "ों", "ें"],
    ["ाकर", "ाइए", "ाईं", "ाया", "ेगी", "ेगा", "ोगी", "ोगे", "ाने", "ाना", "ाते", "ाती", "ाता", "तीं", "ाओं", "ाएं", "ुओं", "ुएं", "ुआं"],
    ["ाएगी", "ाएगा", "ाओगी", "ाओगे", "एंगी", "ेंगी", "एंगे", "ेंगे", "ूंगी", "ूंगा", "ातीं", "नाओं", "नाएं", "ताओं", "ताएं", "ियाँ", "ियों", "ियां"],
    ["ाएंगी", "ाएंगे", "ाऊंगी", "ाऊंगा", "ाइयाँ", "ाइयों", "ाइयां"]
]

_num_words = ["शून्य", "एक", "दो", "तीन", "चार", "पांच", "छह", "सात", "आठ", "नौ", "दस", "ग्यारह", "बारह", "तेरह", "चौदह", "पंद्रह",
              "सोलह", "सत्रह", "अठारह", "उन्नीस", "बीस", "तीस", "चालीस", "पचास", "साठ", "सत्तर", "अस्सी", "नब्बे", "सौ", "हज़ार",
              "लाख", "करोड़", "अरब", "खरब", "नील", "पद्म", "शङ्ख", "गुलशन"]


"""
For Hindi numerals the prefix remains the same for every 10th digit eg. 12, 22, 32, 42 (बारह, बाईस, बतीस, बयालीस...).
Here, the prefix ब or बा , although 89 and 99 are exception from 19 to 79.
Note: Indian Numbering System is based on the Vedic numbering system in which numbers over 9,999 are written in 
two-digit groups rather than the three-digit groups used in most other parts of the world. (1,00,000 = 1 Lakh)
1 arab = 1 billion
1 kharab = 100 billion
1 neel = 10 trillion
1 padma = 1 quadrillion
1 sankh = 1 hundred quadrillion
1 gulshan = 1 quintillion
"""


def norm(string):
    # normalise base exceptions, e.g. punctuation or currency symbols
    if string in BASE_NORMS:
        return BASE_NORMS[string]
    # set stem word as norm, if available, adapted from:
    # http://computing.open.ac.uk/Sites/EACLSouthAsia/Papers/p6-Ramanathan.pdf
    # http://research.variancia.com/hindi_stemmer/
    # https://github.com/taranjeet/hindi-tokenizer/blob/master/HindiTokenizer.py#L142
    for suffix_group in reversed(_stem_suffixes):
        length = len(suffix_group[0])
        if len(string) <= length:
            break
        for suffix in suffix_group:
            if string.endswith(suffix):
                return string[:-length]
    return string


def like_num(text):
    text = text.replace(',', '').replace('.', '')
    if text.isdigit():
        return True
    if text.count('/') == 1:
        num, denom = text.split('/')
        if num.isdigit() and denom.isdigit():
            return True
    if text in _num_words:
        return True
    return False


LEX_ATTRS = {
    NORM: norm,
    LIKE_NUM: like_num
}

# coding: utf8
from __future__ import unicode_literals

from ..norm_exceptions import BASE_NORMS
from ...attrs import NORM, LIKE_NUM


# fmt: off
_stem_suffixes = [
    ["ो", "े", "ू", "ु", "ी", "ि", "ा"],
    ["कर", "ाओ", "िए", "ाई", "ाए", "ने", "नी", "ना", "ते", "ीं", "ती", "ता", "ाँ", "ां", "ों", "ें"],
    ["ाकर", "ाइए", "ाईं", "ाया", "ेगी", "ेगा", "ोगी", "ोगे", "ाने", "ाना", "ाते", "ाती", "ाता", "तीं", "ाओं", "ाएं", "ुओं", "ुएं", "ुआं"],
    ["ाएगी", "ाएगा", "ाओगी", "ाओगे", "एंगी", "ेंगी", "एंगे", "ेंगे", "ूंगी", "ूंगा", "ातीं", "नाओं", "नाएं", "ताओं", "ताएं", "ियाँ", "ियों", "ियां"],
    ["ाएंगी", "ाएंगे", "ाऊंगी", "ाऊंगा", "ाइयाँ", "ाइयों", "ाइयां"]
]

# reference 1: https://en.wikipedia.org/wiki/Indian_numbering_system
# reference 2: https://blogs.transparent.com/hindi/hindi-numbers-1-100/
# reference 3: https://www.mindurhindi.com/basic-words-and-phrases-in-hindi/

_one_to_ten = [
    "शून्य",
    "एक",
    "दो",
    "तीन",
    "चार",
    "पांच", "पाँच",
    "छह",
    "सात",
    "आठ",
    "नौ",
    "दस",
]

_eleven_to_beyond = [
    "ग्यारह",
    "बारह",
    "तेरह",
    "चौदह",
    "पंद्रह",
    "सोलह",
    "सत्रह",
    "अठारह",
    "उन्नीस",
    "बीस",
    "इकीस", "इक्कीस",
    "बाईस",
    "तेइस",
    "चौबीस",
    "पच्चीस",
    "छब्बीस",
    "सताइस", "सत्ताइस",
    "अट्ठाइस",
    "उनतीस",
    "तीस",
    "इकतीस", "इकत्तीस",
    "बतीस", "बत्तीस",
    "तैंतीस",
    "चौंतीस",
    "पैंतीस",
    "छतीस", "छत्तीस",
    "सैंतीस",
    "अड़तीस",
    "उनतालीस", "उनत्तीस",
    "चालीस",
    "इकतालीस",
    "बयालीस",
    "तैतालीस",
    "चवालीस",
    "पैंतालीस",
    "छयालिस",
    "सैंतालीस",
    "अड़तालीस",
    "उनचास",
    "पचास",
    "इक्यावन",
    "बावन",
    "तिरपन", "तिरेपन",
    "चौवन", "चउवन",
    "पचपन", 
    "छप्पन",
    "सतावन", "सत्तावन",
    "अठावन",
    "उनसठ",
    "साठ",
    "इकसठ",
    "बासठ",
    "तिरसठ", "तिरेसठ",
    "चौंसठ",
    "पैंसठ",
    "छियासठ",
    "सड़सठ",
    "अड़सठ",
    "उनहत्तर",
    "सत्तर",
    "इकहत्तर"
    "बहत्तर", 
    "तिहत्तर",
    "चौहत्तर",
    "पचहत्तर",
    "छिहत्तर",
    "सतहत्तर",
    "अठहत्तर",
    "उन्नासी", "उन्यासी"
    "अस्सी",
    "इक्यासी",
    "बयासी",
    "तिरासी",
    "चौरासी",
    "पचासी",
    "छियासी",
    "सतासी",
    "अट्ठासी",
    "नवासी",
    "नब्बे",
    "इक्यानवे",
    "बानवे",
    "तिरानवे",
    "चौरानवे",
    "पचानवे",
    "छियानवे",
    "सतानवे",
    "अट्ठानवे",
    "निन्यानवे",
    "सौ",
    "हज़ार",
    "लाख",
    "करोड़",
    "अरब",
    "खरब",
]

_num_words = _one_to_ten + _eleven_to_beyond

_ordinal_words_one_to_ten = [
    "प्रथम", "पहला",
    "द्वितीय", "दूसरा",
    "तृतीय", "तीसरा",
    "चौथा",
    "पांचवाँ",
    "छठा",
    "सातवाँ",
    "आठवाँ",
    "नौवाँ",
    "दसवाँ",
]
_ordinal_suffix = "वाँ"
# fmt: on

def norm(string):
    # normalise base exceptions,  e.g. punctuation or currency symbols
    if string in BASE_NORMS:
        return BASE_NORMS[string]
    # set stem word as norm,  if available,  adapted from:
    # http://computing.open.ac.uk/Sites/EACLSouthAsia/Papers/p6-Ramanathan.pdf
    # http://research.variancia.com/hindi_stemmer/
    # https://github.com/taranjeet/hindi-tokenizer/blob/master/HindiTokenizer.py#L142
    for suffix_group in reversed(_stem_suffixes):
        length = len(suffix_group[0])
        if len(string) <= length:
            continue
        for suffix in suffix_group:
            if string.endswith(suffix):
                return string[:-length]
    return string


def like_num(text):
    if text.startswith(("+", "-", "±", "~")):
        text = text[1:]
    text = text.replace(",", "").replace(".", "")
    if text.isdigit():
        return True
    if text.count("/") == 1:
        num, denom = text.split("/")
        if num.isdigit() and denom.isdigit():
            return True
    if text.lower() in _num_words:
        return True

    # check ordinal numbers
    # reference: http://www.englishkitab.com/Vocabulary/Numbers.html
    if text in _ordinal_words_one_to_ten:
        return True
    if text.endswith(_ordinal_suffix):
        if text[:-len(_ordinal_suffix)] in _eleven_to_beyond:
            return True
    return False


LEX_ATTRS = {NORM: norm, LIKE_NUM: like_num}

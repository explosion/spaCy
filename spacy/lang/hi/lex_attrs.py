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
# fmt: on

# reference 1:https://en.wikipedia.org/wiki/Indian_numbering_system
# reference 2: https://blogs.transparent.com/hindi/hindi-numbers-1-100/

_num_words = [
    "शून्य",
    "एक",
    "दो",
    "तीन",
    "चार",
    "पांच",
    "छह",
    "सात",
    "आठ",
    "नौ",
    "दस",
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
    "तीस",
    "चालीस",
    "पचास",
    "साठ",
    "सत्तर",
    "अस्सी",
    "नब्बे",
    "सौ",
    "हज़ार",
    "लाख",
    "करोड़",
    "अरब",
    "खरब",
]


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

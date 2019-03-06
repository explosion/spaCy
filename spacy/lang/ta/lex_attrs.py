# coding: utf8
from __future__ import unicode_literals

from ...attrs import LIKE_NUM


_numeral_suffixes = {"பத்து": "பது", "ற்று": "று", "ரத்து": "ரம்", "சத்து": "சம்"}
_num_words = [
    "பூச்சியம்",
    "ஒரு",
    "ஒன்று",
    "இரண்டு",
    "மூன்று",
    "நான்கு",
    "ஐந்து",
    "ஆறு",
    "ஏழு",
    "எட்டு",
    "ஒன்பது",
    "பத்து",
    "பதினொன்று",
    "பன்னிரண்டு",
    "பதின்மூன்று",
    "பதினான்கு",
    "பதினைந்து",
    "பதினாறு",
    "பதினேழு",
    "பதினெட்டு",
    "பத்தொன்பது",
    "இருபது",
    "முப்பது",
    "நாற்பது",
    "ஐம்பது",
    "அறுபது",
    "எழுபது",
    "எண்பது",
    "தொண்ணூறு",
    "நூறு",
    "இருநூறு",
    "முன்னூறு",
    "நாநூறு",
    "ஐநூறு",
    "அறுநூறு",
    "எழுநூறு",
    "எண்ணூறு",
    "தொள்ளாயிரம்",
    "ஆயிரம்",
    "ஒராயிரம்",
    "லட்சம்",
    "மில்லியன்",
    "கோடி",
    "பில்லியன்",
    "டிரில்லியன்",
]


# 20-89 ,90-899,900-99999 and above have different suffixes
def suffix_filter(text):
    # text without numeral suffixes
    for num_suffix in _numeral_suffixes.keys():
        length = len(num_suffix)
        if len(text) < length:
            break
        elif text.endswith(num_suffix):
            return text[:-length] + _numeral_suffixes[num_suffix]
    return text


def like_num(text):
    text = text.replace(",", "").replace(".", "")
    if text.isdigit():
        return True
    if text.count("/") == 1:
        num, denom = text.split("/")
        if num.isdigit() and denom.isdigit():
            return True
    if text.lower() in _num_words:
        return True
    elif suffix_filter(text) in _num_words:
        return True
    return False


LEX_ATTRS = {LIKE_NUM: like_num}

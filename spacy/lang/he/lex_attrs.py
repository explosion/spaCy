# coding: utf8
from __future__ import unicode_literals

from ...attrs import LIKE_NUM

_num_words = [
    "אפס",
    "אחד",
    "אחת",
    "שתיים",
    "שתים",
    "שניים",
    "שנים",
    "שלוש",
    "שלושה",
    "ארבע",
    "ארבעה",
    "חמש",
    "חמישה",
    "שש",
    "שישה",
    "שבע",
    "שבעה",
    "שמונה",
    "תשע",
    "תשעה",
    "עשר",
    "עשרה",
    "אחד עשר",
    "אחת עשרה",
    "שנים עשר",
    "שתים עשרה",
    "שלושה עשר",
    "שלוש עשרה",
    "ארבעה עשר",
    "ארבע עשרה",
    "חמישה עשר",
    "חמש עשרה",
    "ששה עשר",
    "שש עשרה",
    "שבעה עשר",
    "שבע עשרה",
    "שמונה עשר",
    "שמונה עשרה",
    "תשעה עשר",
    "תשע עשרה",
    "עשרים",
    "שלושים",
    "ארבעים",
    "חמישים",
    "שישים",
    "שבעים",
    "שמונים",
    "תשעים",
    "מאה",
    "אלף",
    "מליון",
    "מליארד",
    "טריליון",
]


_ordinal_words = [
    "ראשון",
    "שני",
    "שלישי",
    "רביעי",
    "חמישי",
    "שישי",
    "שביעי",
    "שמיני",
    "תשיעי",
    "עשירי",
]

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
    
    if text in _num_words:
        return True

    # CHeck ordinal number
    if text in _ordinal_words:
        return True
    return False


LEX_ATTRS = {LIKE_NUM: like_num}

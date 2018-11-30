# coding: utf8
from __future__ import unicode_literals

from ...attrs import LIKE_NUM


_num_words = [
    "nolla",
    "yksi",
    "kaksi",
    "kolme",
    "neljä",
    "viisi",
    "kuusi",
    "seitsemän",
    "kahdeksan",
    "yhdeksän",
    "kymmenen",
    "yksitoista",
    "kaksitoista",
    "kolmetoista" "neljätoista",
    "viisitoista",
    "kuusitoista",
    "seitsemäntoista",
    "kahdeksantoista",
    "yhdeksäntoista",
    "kaksikymmentä",
    "kolmekymmentä",
    "neljäkymmentä",
    "viisikymmentä",
    "kuusikymmentä",
    "seitsemänkymmentä",
    "kahdeksankymmentä",
    "yhdeksänkymmentä",
    "sata",
    "tuhat",
    "miljoona",
    "miljardi",
    "triljoona",
]


def like_num(text):
    if text.startswith(("+", "-", "±", "~")):
        text = text[1:]
    text = text.replace(".", "").replace(",", "")
    if text.isdigit():
        return True
    if text.count("/") == 1:
        num, denom = text.split("/")
        if num.isdigit() and denom.isdigit():
            return True
    if text in _num_words:
        return True
    return False


LEX_ATTRS = {LIKE_NUM: like_num}

# coding: utf8
from __future__ import unicode_literals

from ...attrs import LIKE_NUM

_num_words = [
    "нуль",
    "ноль",
    "бер",
    "ике",
    "өч",
    "дүрт",
    "биш",
    "алты",
    "җиде",
    "сигез",
    "тугыз",
    "ун",
    "унбер",
    "унике",
    "унөч",
    "ундүрт",
    "унбиш",
    "уналты",
    "унҗиде",
    "унсигез",
    "унтугыз",
    "егерме",
    "утыз",
    "кырык",
    "илле",
    "алтмыш",
    "җитмеш",
    "сиксән",
    "туксан",
    "йөз",
    "мең",
    "төмән",
    "миллион",
    "миллиард",
    "триллион",
    "триллиард",
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
    return False


LEX_ATTRS = {LIKE_NUM: like_num}

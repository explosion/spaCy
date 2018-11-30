# coding: utf8
from __future__ import unicode_literals

from ...attrs import LIKE_NUM

_num_words = [
    "බින්දුව",
    "බිංදුව",
    "එක",
    "දෙක",
    "තුන",
    "හතර",
    "පහ",
    "හය",
    "හත",
    "අට",
    "නවය",
    "නමය",
    "දහය",
    "එකොළහ",
    "දොළහ",
    "දහතුන",
    "දහහතර",
    "දාහතර",
    "පහළව",
    "පහළොව",
    "දහසය",
    "දහහත",
    "දාහත",
    "දහඅට",
    "දහනවය",
    "විස්ස",
    "තිහ",
    "හතළිහ",
    "පනහ",
    "හැට",
    "හැත්තෑව",
    "අසූව",
    "අනූව",
    "සියය",
    "දහස",
    "දාහ",
    "ලක්ෂය",
    "මිලියනය",
    "කෝටිය",
    "බිලියනය",
    "ට්‍රිලියනය",
]


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
    return False


LEX_ATTRS = {LIKE_NUM: like_num}

# coding: utf8
from __future__ import unicode_literals

from ...attrs import LIKE_NUM

_num_words = [
    "sero",
    "un",
    "dau",
    "dwy",
    "tri",
    "tair",
    "pedwar",
    "pedair",
    "pump",
    "chwech",
    "saith",
    "wyth",
    "naw",
    "deg",
    "un ar ddeg",
    "deuddeg",
    "tri ar ddeg",
    "tair ar ddeg",
    "pedwar ar ddeg",
    "pedair ar ddeg",
    "pymtheg",
    "un ar bymtheg",
    "dau ar bymtheg",
    "dwy ar bymtheg",
    "deunaw",
    "pedwar ar bymtheg"
    "ugain",
    "deg ar hugain"
    "deugain",
    "deg a deugain",
    "trigain",
    "pedwar ugain"
    "cant",
    "mil",
    "miliwn",
    "biliwn",
    "triliwn",
]


_ordinal_words = [
    "cyntaf",
    "ail",
    "trydydd",
    "trydedd",
    "pedwerydd",
    "pedwaredd",
    "pumed",
    "chweched",
    "seithfed",
    "wythfed",
    "nawfed",
    "degfed",
    "unfed ar ddeg",
    "deuddegfed",
    "trydydd ar ddeg",
    "trydedd ar ddeg",
    "pedwerydd ar ddeg",
    "pedwaredd ar ddeg",
    "pymthegfed",
    "unfed ar bymtheg",
    "ail ar bymtheg",
    "deunawfed",
    "pedwerydd ar bymtheg",
    "ugeinfed",
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

    text_lower = text.lower()
    if text_lower in _num_words:
        return True

    # Check ordinal number
    if text_lower in _ordinal_words:
        return True
    if text_lower.endswith('eg'):
        if text_lower[:-2].isdigit():
            return True
    if text_lower.endswith('fed') or text_lower.endswith('ain'):
        if text_lower[:-3].isdigit():
            return True

    return False


LEX_ATTRS = {LIKE_NUM: like_num}

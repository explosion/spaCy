# coding: utf8
from __future__ import unicode_literals

import unicodedata

from ...attrs import LIKE_NUM


_num_words = [
    "ení",
    "oókàn",
    "ọ̀kanlá",
    "ẹ́ẹdọ́gbọ̀n",
    "àádọ́fà",
    "ẹ̀walélúɡba",
    "egbèje",
    "ẹgbàárin",
    "èjì",
    "eéjì",
    "èjìlá",
    "ọgbọ̀n,",
    "ọgọ́fà",
    "ọ̀ọ́dúrún",
    "ẹgbẹ̀jọ",
    "ẹ̀ẹ́dẹ́ɡbàárùn",
    "ẹ̀ta",
    "ẹẹ́ta",
    "ẹ̀talá",
    "aárùndílogójì",
    "àádóje",
    "irinwó",
    "ẹgbẹ̀sàn",
    "ẹgbàárùn",
    "ẹ̀rin",
    "ẹẹ́rin",
    "ẹ̀rinlá",
    "ogójì",
    "ogóje",
    "ẹ̀ẹ́dẹ́gbẹ̀ta",
    "ẹgbàá",
    "ẹgbàájọ",
    "àrún",
    "aárùn",
    "ẹ́ẹdógún",
    "àádọ́ta",
    "àádọ́jọ",
    "ẹgbẹ̀ta",
    "ẹgboókànlá",
    "ẹgbàawǎ",
    "ẹ̀fà",
    "ẹẹ́fà",
    "ẹẹ́rìndílógún",
    "ọgọ́ta",
    "ọgọ́jọ",
    "ọ̀ọ́dẹ́gbẹ̀rin",
    "ẹgbẹ́ẹdógún",
    "ọkẹ́marun",
    "èje",
    "etàdílógún",
    "àádọ́rin",
    "àádọ́sán",
    "ẹgbẹ̀rin",
    "ẹgbàajì",
    "ẹgbẹ̀ẹgbẹ̀rún",
    "ẹ̀jọ",
    "ẹẹ́jọ",
    "eéjìdílógún",
    "ọgọ́rin",
    "ọgọsàn",
    "ẹ̀ẹ́dẹ́gbẹ̀rún",
    "ẹgbẹ́ẹdọ́gbọ̀n",
    "ọgọ́rùn ọkẹ́",
    "ẹ̀sán",
    "ẹẹ́sàn",
    "oókàndílógún",
    "àádọ́rùn",
    "ẹ̀wadilúɡba",
    "ẹgbẹ̀rún",
    "ẹgbàáta",
    "ẹ̀wá",
    "ẹẹ́wàá",
    "ogún",
    "ọgọ́rùn",
    "igba",
    "ẹgbẹ̀fà",
    "ẹ̀ẹ́dẹ́ɡbarin",
]


def strip_accents_text(text):
    """
    Converts the string to NFD, separates & returns only the base characters
    :param text:
    :return: input string without diacritic adornments on base characters
    """
    return "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )


def like_num(text):
    text = text.replace(",", "").replace(".", "")
    num_markers = ["dí", "dọ", "lé", "dín", "di", "din", "le", "do"]
    if any(mark in text for mark in num_markers):
        return True
    text = strip_accents_text(text)
    _num_words_stripped = [strip_accents_text(num) for num in _num_words]
    if text.isdigit():
        return True
    if text in _num_words_stripped or text.lower() in _num_words_stripped:
        return True
    return False


LEX_ATTRS = {LIKE_NUM: like_num}

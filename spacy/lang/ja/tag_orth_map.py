# encoding: utf8
from __future__ import unicode_literals

from ...symbols import POS, ADJ, AUX, DET, PART, PRON, SPACE ,X

# mapping from tag bi-gram to pos of previous token
TAG_ORTH_MAP = {
    "空白": {
        " ": SPACE,
        "　": X,
    },
    "助詞-副助詞": {
        "たり": PART,
    },
    "連体詞": {
        "あの": DET,
        "かの": DET,
        "この": DET,
        "その": DET,
        "どの": DET,
        "彼の": DET,
        "此の": DET,
        "其の": DET,
        "ある": PRON,
        "こんな": PRON,
        "そんな": PRON,
        "どんな": PRON,
        "あらゆる": PRON,
    },
}

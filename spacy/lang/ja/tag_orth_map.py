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
        "こ": PRON,
        "そ": PRON,
        "あ": PRON,
        "ど": PRON,
        "此": PRON,
        "其": PRON,
        "彼": PRON,
    },
}

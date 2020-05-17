# encoding: utf8
from __future__ import unicode_literals

from ...symbols import POS, ADJ, AUX, VERB

# mapping from tag bi-gram to pos of previous token
TAG_BIGRAM_MAP = {
    # This covers only small part of AUX.
    ("形容詞-非自立可能", "助詞-終助詞"): AUX,
    # This covers acl, advcl, obl and root, but has side effect for compound.
    ("名詞-普通名詞-サ変可能", "動詞-非自立可能"): VERB,
    # This covers almost all of the deps
    ("名詞-普通名詞-サ変形状詞可能", "動詞-非自立可能"): VERB,
    # This covers root but has small side effect for advcl
    ("名詞-普通名詞-形状詞可能", "助動詞"): ADJ,
}

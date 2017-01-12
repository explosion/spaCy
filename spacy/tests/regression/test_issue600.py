# coding: utf-8
from __future__ import unicode_literals

from ...vocab import Vocab
from ..util import get_doc


def test_issue600():
    vocab = Vocab(tag_map={'NN': {'pos': 'NOUN'}})
    doc = get_doc(vocab, ["hello"])
    doc[0].tag_ = 'NN'

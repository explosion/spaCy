from __future__ import unicode_literals
from ...tokens import Doc
from ...vocab import Vocab
from ...attrs import POS


def test_issue600():
    doc = Doc(Vocab(tag_map={'NN': {'pos': 'NOUN'}}), words=['hello'])
    doc[0].tag_ = u'NN'

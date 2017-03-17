# coding: utf8
from __future__ import unicode_literals
from ...vocab import Vocab
from ...tokens.doc import Doc


def test_token_is_hashable():
    doc = Doc(Vocab(), ['hello', 'world'])
    token = doc[0]
    s = set([token])
    items = list(s)
    assert items[0] is token

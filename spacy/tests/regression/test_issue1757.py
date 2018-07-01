'''Test comparison against None doesn't cause segfault'''
from __future__ import unicode_literals

from ...tokens import Doc
from ...vocab import Vocab

def test_issue1757():
    doc = Doc(Vocab(), words=['a', 'b', 'c'])
    assert not doc[0] < None
    assert not doc[0] == None
    assert doc[0] >= None
    span = doc[:2]
    assert not span < None
    assert not span == None
    assert span >= None
    lex = doc.vocab['a']
    assert not lex == None
    assert not lex < None

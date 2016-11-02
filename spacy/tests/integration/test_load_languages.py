# encoding: utf8
from __future__ import unicode_literals
from ...fr import French

def test_load_french():
    nlp = French()
    doc = nlp(u'Parlez-vous français?')
    assert doc[0].text == u'Parlez'
    assert doc[1].text == u'-'
    assert doc[2].text == u'vous'
    assert doc[3].text == u'français'
    assert doc[4].text == u'?'

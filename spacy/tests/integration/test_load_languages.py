# encoding: utf8
from __future__ import unicode_literals
from ...fr import French

def test_load_french():
    nlp = French()
    doc = nlp(u'Parlez-vous français?')

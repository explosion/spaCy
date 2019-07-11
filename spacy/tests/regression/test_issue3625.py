# coding: utf8
from __future__ import unicode_literals

from spacy.lang.hi import Hindi

def test_issue3625():
    """Test that default punctuation rules applies to hindi unicode characters"""
    nlp = Hindi()
    doc = nlp(u"hi. how हुए. होटल, होटल")
    assert [token.text for token in doc] == ['hi', '.', 'how', 'हुए', '.', 'होटल', ',', 'होटल']
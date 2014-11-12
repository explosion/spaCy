from __future__ import unicode_literals

from spacy.en import EN

def test1():
    words = ['JAPAN', 'GET', 'LUCKY']
    tokens = EN.tokens_from_list(words)
    assert len(tokens) == 3
    assert tokens[0].string == 'JAPAN'

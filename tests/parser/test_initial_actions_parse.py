import pytest


def test_initial(EN):
    doc = EN.tokenizer(u'I ate the pizza with anchovies.')
    EN.tagger(doc)
    EN.parser(doc, initial_actions=['L-nsubj', 'S', 'L-det'])
    assert doc[0].head.i == 1

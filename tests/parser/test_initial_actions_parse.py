import pytest


@pytest.mark.models
def test_initial(EN):
    doc = EN.tokenizer(u'I ate the pizza with anchovies.')
    EN.tagger(doc)
    next_actions = EN.parser.partial(doc, ['L-nsubj', 'S', 'L-det'])
    assert doc[0].head.i == 1
    assert doc[1].head.i == 1
    assert doc[2].head.i == 3
    assert doc[3].head.i == 3
    assert doc

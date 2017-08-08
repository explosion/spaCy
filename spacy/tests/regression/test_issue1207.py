from __future__ import unicode_literals
from ..util import get_doc
from ...vocab import Vocab
from ...en import English


def test_span_noun_chunks():
    vocab = Vocab(lang='en', tag_map=English.Defaults.tag_map)
    words = "Employees are recruiting talented staffers from overseas .".split()
    heads = [1, 1, 0, 1, -2, -1, -5]
    deps = ['nsubj', 'aux', 'ROOT', 'nmod', 'dobj', 'adv', 'pobj']
    tags = ['NNS', 'VBP', 'VBG', 'JJ', 'NNS', 'IN', 'NN', '.']
    doc = get_doc(vocab, words=words, heads=heads, deps=deps, tags=tags)
    doc.is_parsed = True
    
    noun_chunks = [np.text for np in doc.noun_chunks]
    assert noun_chunks == ['Employees', 'talented staffers', 'overseas']

    span = doc[0:4]
    noun_chunks = [np.text for np in span.noun_chunks]
    assert noun_chunks == ['Employees']

    for sent in doc.sents:
        noun_chunks = [np.text for np in sent.noun_chunks]
        assert noun_chunks == ['Employees', 'talented staffers', 'overseas']

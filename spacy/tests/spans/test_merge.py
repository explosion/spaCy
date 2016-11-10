from __future__ import unicode_literals
from spacy.attrs import HEAD
import pytest
import numpy


def test_merge_tokens(EN):
    tokens = EN(u'Los Angeles start.')
    tokens.from_array([HEAD], numpy.asarray([[1, 1, 0, -1]], dtype='int32').T)
    assert len(tokens) == 4
    assert tokens[0].head.orth_ == 'Angeles'
    assert tokens[1].head.orth_ == 'start'
    tokens.merge(0, len('Los Angeles'), 'NNP', 'Los Angeles', 'GPE')
    assert len(tokens) == 3
    assert tokens[0].orth_ == 'Los Angeles'
    assert tokens[0].head.orth_ == 'start'


@pytest.mark.models
def test_merge_heads(EN):
    tokens = EN(u'I found a pilates class near work.')
    assert len(tokens) == 8
    tokens.merge(tokens[3].idx, tokens[4].idx + len(tokens[4]), tokens[4].tag_,
                 'pilates class', 'O')
    assert len(tokens) == 7
    assert tokens[0].head.i == 1
    assert tokens[1].head.i == 1
    assert tokens[2].head.i == 3
    assert tokens[3].head.i == 1
    assert tokens[4].head.i in [1, 3]
    assert tokens[5].head.i == 4


@pytest.mark.models
def test_issue_54(EN):
    text = u'Talks given by women had a slightly higher number of questions asked (3.2$\pm$0.2) than talks given by men (2.6$\pm$0.1).'
    tokens = EN(text)


@pytest.mark.models
def test_np_merges(EN):
    text = u'displaCy is a parse tool built with Javascript'
    tokens = EN(text)
    assert tokens[4].head.i == 1
    tokens.merge(tokens[2].idx, tokens[4].idx + len(tokens[4]), u'NP', u'tool', u'O')
    assert tokens[2].head.i == 1
    tokens = EN('displaCy is a lightweight and modern dependency parse tree visualization tool built with CSS3 and JavaScript.')
    
    ents = [(e[0].idx, e[-1].idx + len(e[-1]), e.label_, e.lemma_)
            for e in tokens.ents]
    for start, end, label, lemma in ents:
        merged = tokens.merge(start, end, label, lemma, label)
        assert merged != None, (start, end, label, lemma) 


    tokens = EN(u'One test with entities like New York City so the ents list is not void')

    for span in tokens.ents:
        merged = span.merge()
        assert merged != None, (span.start, span.end, span.label_, span.lemma_) 

@pytest.mark.models
def test_entity_merge(EN):
    tokens = EN(u'Stewart Lee is a stand up comedian who lives in England and loves Joe Pasquale.\n')
    assert(len(tokens) == 17)
    for ent in tokens.ents:
        label, lemma, type_ = (ent.root.tag_, ent.root.lemma_, max(w.ent_type_ for w in ent))
        ent.merge(label, lemma, type_)
    # check looping is ok
    assert(len(tokens) == 15)


@pytest.mark.models
def test_sentence_update_after_merge(EN):
    tokens = EN(u'Stewart Lee is a stand up comedian. He lives in England and loves Joe Pasquale.')
    sent1, sent2 = list(tokens.sents)
    init_len = len(sent1)
    init_len2 = len(sent2)
    merge_me = tokens[0:2]
    merge_me.merge(u'none', u'none', u'none')
    merge_me2 = tokens[-2:]
    merge_me2.merge(u'none', u'none', u'none')
    assert(len(sent1) == init_len - 1)
    assert(len(sent2) == init_len2 - 1)


@pytest.mark.models
def test_subtree_size_check(EN):
    tokens = EN(u'Stewart Lee is a stand up comedian who lives in England and loves Joe Pasquale')
    sent1 = list(tokens.sents)[0]
    init_len = len(list(sent1.root.subtree))
    merge_me = tokens[0:2]
    merge_me.merge(u'none', u'none', u'none')
    assert(len(list(sent1.root.subtree)) == init_len - 1)

# coding: utf-8
from __future__ import unicode_literals

from ..util import get_doc, apply_transition_sequence

import pytest


def test_parser_root(en_tokenizer):
    text = "i don't have other assistance"
    heads = [3, 2, 1, 0, 1, -2]
    deps = ['nsubj', 'aux', 'neg', 'ROOT', 'amod', 'dobj']
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], heads=heads, deps=deps)
    for t in doc:
        assert t.dep != 0, t.text


@pytest.mark.parametrize('text', ["Hello"])
def test_parser_parse_one_word_sentence(en_tokenizer, en_parser, text):
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], heads=[0], deps=['ROOT'])

    assert len(doc) == 1
    with en_parser.step_through(doc) as _:
        pass
    assert doc[0].dep != 0


def test_parser_initial(en_tokenizer, en_parser):
    text = "I ate the pizza with anchovies."
    heads = [1, 0, 1, -2, -3, -1, -5]
    transition = ['L-nsubj', 'S', 'L-det']

    tokens = en_tokenizer(text)
    apply_transition_sequence(en_parser, tokens, transition)

    assert tokens[0].head.i == 1
    assert tokens[1].head.i == 1
    assert tokens[2].head.i == 3
    assert tokens[3].head.i == 3


def test_parser_parse_subtrees(en_tokenizer, en_parser):
    text = "The four wheels on the bus turned quickly"
    heads = [2, 1, 4, -1, 1, -2, 0, -1]
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], heads=heads)

    assert len(list(doc[2].lefts)) == 2
    assert len(list(doc[2].rights)) == 1
    assert len(list(doc[2].children)) == 3
    assert len(list(doc[5].lefts)) == 1
    assert len(list(doc[5].rights)) == 0
    assert len(list(doc[5].children)) == 1
    assert len(list(doc[2].subtree)) == 6


def test_parser_merge_pp(en_tokenizer):
    text = "A phrase with another phrase occurs"
    heads = [1, 4, -1, 1, -2, 0]
    deps = ['det', 'nsubj', 'prep', 'det', 'pobj', 'ROOT']
    tags = ['DT', 'NN', 'IN', 'DT', 'NN', 'VBZ']

    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], deps=deps, heads=heads, tags=tags)
    nps = [(np[0].idx, np[-1].idx + len(np[-1]), np.lemma_) for np in doc.noun_chunks]

    for start, end, lemma in nps:
        doc.merge(start, end, label='NP', lemma=lemma)
    assert doc[0].text == 'A phrase'
    assert doc[1].text == 'with'
    assert doc[2].text == 'another phrase'
    assert doc[3].text == 'occurs'


def test_parser_arc_eager_finalize_state(en_tokenizer, en_parser):
    text = "a b c d e"

    # right branching
    transition = ['R-nsubj', 'D', 'R-nsubj', 'R-nsubj', 'D', 'R-ROOT']
    tokens = en_tokenizer(text)
    apply_transition_sequence(en_parser, tokens, transition)

    assert tokens[0].n_lefts == 0
    assert tokens[0].n_rights == 2
    assert tokens[0].left_edge.i == 0
    assert tokens[0].right_edge.i == 4
    assert tokens[0].head.i == 0

    assert tokens[1].n_lefts == 0
    assert tokens[1].n_rights == 0
    assert tokens[1].left_edge.i == 1
    assert tokens[1].right_edge.i == 1
    assert tokens[1].head.i == 0

    assert tokens[2].n_lefts == 0
    assert tokens[2].n_rights == 2
    assert tokens[2].left_edge.i == 2
    assert tokens[2].right_edge.i == 4
    assert tokens[2].head.i == 0

    assert tokens[3].n_lefts == 0
    assert tokens[3].n_rights == 0
    assert tokens[3].left_edge.i == 3
    assert tokens[3].right_edge.i == 3
    assert tokens[3].head.i == 2

    assert tokens[4].n_lefts == 0
    assert tokens[4].n_rights == 0
    assert tokens[4].left_edge.i == 4
    assert tokens[4].right_edge.i == 4
    assert tokens[4].head.i == 2

    # left branching
    transition = ['S', 'S', 'S', 'L-nsubj','L-nsubj','L-nsubj', 'L-nsubj']
    tokens = en_tokenizer(text)
    apply_transition_sequence(en_parser, tokens, transition)

    assert tokens[0].n_lefts == 0
    assert tokens[0].n_rights == 0
    assert tokens[0].left_edge.i == 0
    assert tokens[0].right_edge.i == 0
    assert tokens[0].head.i == 4

    assert tokens[1].n_lefts == 0
    assert tokens[1].n_rights == 0
    assert tokens[1].left_edge.i == 1
    assert tokens[1].right_edge.i == 1
    assert tokens[1].head.i == 4

    assert tokens[2].n_lefts == 0
    assert tokens[2].n_rights == 0
    assert tokens[2].left_edge.i == 2
    assert tokens[2].right_edge.i == 2
    assert tokens[2].head.i == 4

    assert tokens[3].n_lefts == 0
    assert tokens[3].n_rights == 0
    assert tokens[3].left_edge.i == 3
    assert tokens[3].right_edge.i == 3
    assert tokens[3].head.i == 4

    assert tokens[4].n_lefts == 4
    assert tokens[4].n_rights == 0
    assert tokens[4].left_edge.i == 0
    assert tokens[4].right_edge.i == 4
    assert tokens[4].head.i == 4

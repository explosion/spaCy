# coding: utf-8
from __future__ import unicode_literals

import pytest

from ..util import get_doc, apply_transition_sequence


def test_parser_root(en_tokenizer):
    text = "i don't have other assistance"
    heads = [3, 2, 1, 0, 1, -2]
    deps = ["nsubj", "aux", "neg", "ROOT", "amod", "dobj"]
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, words=[t.text for t in tokens], heads=heads, deps=deps)
    for t in doc:
        assert t.dep != 0, t.text


@pytest.mark.xfail
@pytest.mark.parametrize("text", ["Hello"])
def test_parser_parse_one_word_sentence(en_tokenizer, en_parser, text):
    tokens = en_tokenizer(text)
    doc = get_doc(
        tokens.vocab, words=[t.text for t in tokens], heads=[0], deps=["ROOT"]
    )

    assert len(doc) == 1
    with en_parser.step_through(doc) as _:  # noqa: F841
        pass
    assert doc[0].dep != 0


@pytest.mark.xfail
def test_parser_initial(en_tokenizer, en_parser):
    text = "I ate the pizza with anchovies."
    # heads = [1, 0, 1, -2, -3, -1, -5]
    transition = ["L-nsubj", "S", "L-det"]
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
    doc = get_doc(tokens.vocab, words=[t.text for t in tokens], heads=heads)
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
    deps = ["det", "nsubj", "prep", "det", "pobj", "ROOT"]
    tags = ["DT", "NN", "IN", "DT", "NN", "VBZ"]
    tokens = en_tokenizer(text)
    doc = get_doc(
        tokens.vocab, words=[t.text for t in tokens], deps=deps, heads=heads, tags=tags
    )
    with doc.retokenize() as retokenizer:
        for np in doc.noun_chunks:
            retokenizer.merge(np, attrs={"lemma": np.lemma_})
    assert doc[0].text == "A phrase"
    assert doc[1].text == "with"
    assert doc[2].text == "another phrase"
    assert doc[3].text == "occurs"


@pytest.mark.xfail
def test_parser_arc_eager_finalize_state(en_tokenizer, en_parser):
    text = "a b c d e"

    # right branching
    transition = ["R-nsubj", "D", "R-nsubj", "R-nsubj", "D", "R-ROOT"]
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
    transition = ["S", "S", "S", "L-nsubj", "L-nsubj", "L-nsubj", "L-nsubj"]
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


def test_parser_set_sent_starts(en_vocab):
    # fmt: off
    words = ['Ein', 'Satz', '.', 'Außerdem', 'ist', 'Zimmer', 'davon', 'überzeugt', ',', 'dass', 'auch', 'epige-', '\n', 'netische', 'Mechanismen', 'eine', 'Rolle', 'spielen', ',', 'also', 'Vorgänge', ',', 'die', '\n', 'sich', 'darauf', 'auswirken', ',', 'welche', 'Gene', 'abgelesen', 'werden', 'und', '\n', 'welche', 'nicht', '.', '\n']
    heads = [1, 0, -1, 27, 0, -1, 1, -3, -1, 8, 4, 3, -1, 1, 3, 1, 1, -11, -1, 1, -9, -1, 4, -1, 2, 1, -6, -1, 1, 2, 1, -6, -1, -1, -17, -31, -32, -1]
    deps = ['nk', 'ROOT', 'punct', 'mo', 'ROOT', 'sb', 'op', 'pd', 'punct', 'cp', 'mo', 'nk', '', 'nk', 'sb', 'nk', 'oa', 're', 'punct', 'mo', 'app', 'punct', 'sb', '', 'oa', 'op', 'rc', 'punct', 'nk', 'sb', 'oc', 're', 'cd', '', 'oa', 'ng', 'punct', '']
    # fmt: on
    doc = get_doc(en_vocab, words=words, deps=deps, heads=heads)
    for i in range(len(words)):
        if i == 0 or i == 3:
            assert doc[i].is_sent_start is True
        else:
            assert doc[i].is_sent_start is None
    for sent in doc.sents:
        for token in sent:
            assert token.head in sent

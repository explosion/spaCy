from __future__ import unicode_literals

import pytest


@pytest.mark.models
def test_root(EN):
    tokens = EN(u"i don't have other assistance")
    for t in tokens:
        assert t.dep != 0, t.orth_


@pytest.mark.models
def test_one_word_sentence(EN):
    # one word sentence
    doc = EN.tokenizer.tokens_from_list(['Hello'])
    EN.tagger(doc)
    assert len(doc) == 1
    with EN.parser.step_through(doc) as _:
        pass
    assert doc[0].dep != 0


def apply_transition_sequence(model, doc, sequence):
    for action_name in sequence:
        if '-' in action_name:
            move, label = action_name.split('-')
            model.parser.add_label(label)
    with model.parser.step_through(doc) as stepwise:
        for transition in sequence:
            stepwise.transition(transition)


@pytest.mark.models
def test_arc_eager_finalize_state(EN):
    # right branching
    example = EN.tokenizer.tokens_from_list(u"a b c d e".split(' '))
    apply_transition_sequence(EN, example, ['R-nsubj','D','R-nsubj','R-nsubj','D','R-ROOT'])

    assert example[0].n_lefts == 0
    assert example[0].n_rights == 2
    assert example[0].left_edge.i == 0
    assert example[0].right_edge.i == 4
    assert example[0].head.i == 0

    assert example[1].n_lefts == 0
    assert example[1].n_rights == 0
    assert example[1].left_edge.i == 1
    assert example[1].right_edge.i == 1
    assert example[1].head.i == 0

    assert example[2].n_lefts == 0
    assert example[2].n_rights == 2
    assert example[2].left_edge.i == 2
    assert example[2].right_edge.i == 4
    assert example[2].head.i == 0

    assert example[3].n_lefts == 0
    assert example[3].n_rights == 0
    assert example[3].left_edge.i == 3
    assert example[3].right_edge.i == 3
    assert example[3].head.i == 2

    assert example[4].n_lefts == 0
    assert example[4].n_rights == 0
    assert example[4].left_edge.i == 4
    assert example[4].right_edge.i == 4
    assert example[4].head.i == 2

    # left branching
    example = EN.tokenizer.tokens_from_list(u"a b c d e".split(' '))
    apply_transition_sequence(EN, example, ['S', 'S', 'S', 'L-nsubj','L-nsubj','L-nsubj', 'L-nsubj'])

    assert example[0].n_lefts == 0
    assert example[0].n_rights == 0
    assert example[0].left_edge.i == 0
    assert example[0].right_edge.i == 0
    assert example[0].head.i == 4

    assert example[1].n_lefts == 0
    assert example[1].n_rights == 0
    assert example[1].left_edge.i == 1
    assert example[1].right_edge.i == 1
    assert example[1].head.i == 4

    assert example[2].n_lefts == 0
    assert example[2].n_rights == 0
    assert example[2].left_edge.i == 2
    assert example[2].right_edge.i == 2
    assert example[2].head.i == 4

    assert example[3].n_lefts == 0
    assert example[3].n_rights == 0
    assert example[3].left_edge.i == 3
    assert example[3].right_edge.i == 3
    assert example[3].head.i == 4

    assert example[4].n_lefts == 4
    assert example[4].n_rights == 0
    assert example[4].left_edge.i == 0
    assert example[4].right_edge.i == 4
    assert example[4].head.i == 4

# coding: utf-8
from __future__ import unicode_literals

from ..util import get_doc

import pytest


@pytest.fixture
def text():
    return u"""
It was a bright cold day in April, and the clocks were striking thirteen.
Winston Smith, his chin nuzzled into his breast in an effort to escape the
vile wind, slipped quickly through the glass doors of Victory Mansions,
though not quickly enough to prevent a swirl of gritty dust from entering
along with him.

The hallway smelt of boiled cabbage and old rag mats. At one end of it a
coloured poster, too large for indoor display, had been tacked to the wall.
It depicted simply an enormous face, more than a metre wide: the face of a
man of about forty-five, with a heavy black moustache and ruggedly handsome
features. Winston made for the stairs. It was no use trying the lift. Even at
the best of times it was seldom working, and at present the electric current
was cut off during daylight hours. It was part of the economy drive in
preparation for Hate Week. The flat was seven flights up, and Winston, who
was thirty-nine and had a varicose ulcer above his right ankle, went slowly,
resting several times on the way. On each landing, opposite the lift-shaft,
the poster with the enormous face gazed from the wall. It was one of those
pictures which are so contrived that the eyes follow you about when you move.
BIG BROTHER IS WATCHING YOU, the caption beneath it ran.
"""


@pytest.fixture
def heads():
    return [1, 1, 0, 3, 2, 1, -4, -1, -1, -7, -8, 1, -10, 2, 1, -3, -1, -15,
            -1, 1, 4, -1, 1, -3, 0, -1, 1, -2, -4, 1, -2, 1, -2, 3, -1, 1,
            -4, -13, -14, -1, -2, 2, 1, -3, -1, 1, -2, -9, -1, 3, 1, 1, -14,
            1, -2, 1, -2, -1, 1, -2, -6, -1, -1, -2, -1, -1, -42, -1, 2, 1,
            0, -1, 1, -2, -1, 2, 1, -4, -8, 0, 1, -2, -1, -1, 3, -1, 1, -6,
            9, 1, 7, -1, 1, -2, 3, 2, 1, -10, -1, 1, -2, -22, -1, 1, 0, -1,
            2, 1, -4, -1, -2, -1, 1, -2, -6, -7, 1, -9, -1, 2, -1, -3, -1,
            3, 2, 1, -4, -19, -24, 3, 2, 1, -4, -1, 1, 2, -1, -5, -34, 1, 0,
            -1, 1, -2, -4, 1, 0, 1, -2, -1, 1, -2, -6, 1, 9, -1, 1, -3, -1,
            -1, 3, 2, 1, 0, -1, -2, 7, -1, 5, 1, 3, -1, 1, -10, -1, -2, 1,
            -2, -15, 1, 0, -1, -1, 2, 1, -3, -1, -1, -2, -1, 1, -2, -12, 1,
            1, 0, 1, -2, -1, -2, -3, 9, -1, 2, -1, -4, 2, 1, -3, -4, -15, 2,
            1, -3, -1, 2, 1, -3, -8, -9, -1, -2, -1, -4, 1, -2, -3, 1, -2,
            -19, 17, 1, -2, 14, 13, 3, 2, 1, -4, 8, -1, 1, 5, -1, 2, 1, -3,
            0, -1, 1, -2, -4, 1, 0, -1, -1, 2, -1, -3, 1, -2, 1, -2, 3, 1,
            1, -4, -1, -2, 2, 1, -5, -19, -1, 1, 1, 0, 1, 6, -1, 1, -3, -1,
            -1, -8, -9, -1]


def test_parser_parse_navigate_consistency(en_tokenizer, text, heads):
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], heads=heads)
    for head in doc:
        for child in head.lefts:
            assert child.head is head
        for child in head.rights:
            assert child.head is head


def test_parser_parse_navigate_child_consistency(en_tokenizer, text, heads):
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], heads=heads)

    lefts = {}
    rights = {}
    for head in doc:
        assert head.i not in lefts
        lefts[head.i] = set()
        for left in head.lefts:
            lefts[head.i].add(left.i)
        assert head.i not in rights
        rights[head.i] = set()
        for right in head.rights:
            rights[head.i].add(right.i)
    for head in doc:
        assert head.n_rights == len(rights[head.i])
        assert head.n_lefts == len(lefts[head.i])
    for child in doc:
        if child.i < child.head.i:
            assert child.i in lefts[child.head.i]
            assert child.i not in rights[child.head.i]
            lefts[child.head.i].remove(child.i)
        elif child.i > child.head.i:
            assert child.i in rights[child.head.i]
            assert child.i not in lefts[child.head.i]
            rights[child.head.i].remove(child.i)
    for head_index, children in lefts.items():
        assert not children
    for head_index, children in rights.items():
        assert not children


def test_parser_parse_navigate_edges(en_tokenizer, text, heads):
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], heads=heads)
    for token in doc:
        subtree = list(token.subtree)
        debug = '\t'.join((token.text, token.left_edge.text, subtree[0].text))
        assert token.left_edge == subtree[0], debug
        debug = '\t'.join((token.text, token.right_edge.text, subtree[-1].text, token.right_edge.head.text))
        assert token.right_edge == subtree[-1], debug

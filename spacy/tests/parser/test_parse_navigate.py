from __future__ import unicode_literals
from os import path
import io

import pytest


@pytest.fixture
def sun_text():
    with io.open(path.join(path.dirname(__file__), '..', 'sun.txt'), 'r',
                 encoding='utf8') as file_:
        text = file_.read()
    return text


@pytest.mark.models
def test_consistency(EN, sun_text):
    tokens = EN(sun_text)
    for head in tokens:
        for child in head.lefts:
            assert child.head is head
        for child in head.rights:
            assert child.head is head


@pytest.mark.models
def test_child_consistency(EN, sun_text):
    tokens = EN(sun_text)

    lefts = {}
    rights = {}
    for head in tokens:
        assert head.i not in lefts
        lefts[head.i] = set()
        for left in head.lefts:
            lefts[head.i].add(left.i)
        assert head.i not in rights
        rights[head.i] = set()
        for right in head.rights:
            rights[head.i].add(right.i)
    for head in tokens:
        assert head.n_rights == len(rights[head.i])
        assert head.n_lefts == len(lefts[head.i])
    for child in tokens:
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


@pytest.mark.models
def test_edges(EN, sun_text):
    tokens = EN(sun_text)
    for token in tokens:
        subtree = list(token.subtree)
        debug = '\t'.join((token.orth_, token.left_edge.orth_, subtree[0].orth_))
        assert token.left_edge == subtree[0], debug
        debug = '\t'.join((token.orth_, token.right_edge.orth_, subtree[-1].orth_, token.right_edge.head.orth_))
        assert token.right_edge == subtree[-1], debug

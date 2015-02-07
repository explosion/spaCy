from __future__ import unicode_literals
from os import path
import codecs

from spacy.en import English

import pytest


@pytest.fixture
def sun_text():
    with codecs.open(path.join(path.dirname(__file__), 'sun.txt'), 'r', 'utf8') as file_:
        text = file_.read()
    return text


@pytest.fixture
def nlp():
    return English()


def test_consistency(nlp, sun_text):
    tokens = nlp(sun_text)
    for head in tokens:
        for child in head.lefts:
            assert child.head is head
        for child in head.rights:
            assert child.head is head


def test_child_consistency(nlp, sun_text):
    tokens = nlp(sun_text)

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


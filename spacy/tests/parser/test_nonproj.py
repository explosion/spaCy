# coding: utf-8
from __future__ import unicode_literals

from ...syntax.nonproj import ancestors, contains_cycle, is_nonproj_arc
from ...syntax.nonproj import is_nonproj_tree, PseudoProjectivity
from ...attrs import DEP, HEAD
from ..util import get_doc

import pytest


@pytest.fixture
def tree():
    return [1, 2, 2, 4, 5, 2, 2]

@pytest.fixture
def cyclic_tree():
    return [1, 2, 2, 4, 5, 3, 2]

@pytest.fixture
def partial_tree():
    return [1, 2, 2, 4, 5, None, 7, 4, 2]

@pytest.fixture
def nonproj_tree():
    return [1, 2, 2, 4, 5, 2, 7, 4, 2]

@pytest.fixture
def proj_tree():
    return [1, 2, 2, 4, 5, 2, 7, 5, 2]

@pytest.fixture
def multirooted_tree():
    return [3, 2, 0, 3, 3, 7, 7, 3, 7, 10, 7, 10, 11, 12, 18, 16, 18, 17, 12, 3]


def test_parser_ancestors(tree, cyclic_tree, partial_tree, multirooted_tree):
    assert([a for a in ancestors(3, tree)] == [4, 5, 2])
    assert([a for a in ancestors(3, cyclic_tree)] == [4, 5, 3, 4, 5, 3, 4])
    assert([a for a in ancestors(3, partial_tree)] == [4, 5, None])
    assert([a for a in ancestors(17, multirooted_tree)] == [])


def test_parser_contains_cycle(tree, cyclic_tree, partial_tree, multirooted_tree):
    assert(contains_cycle(tree) == None)
    assert(contains_cycle(cyclic_tree) == set([3, 4, 5]))
    assert(contains_cycle(partial_tree) == None)
    assert(contains_cycle(multirooted_tree) == None)


def test_parser_is_nonproj_arc(nonproj_tree, partial_tree, multirooted_tree):
    assert(is_nonproj_arc(0, nonproj_tree) == False)
    assert(is_nonproj_arc(1, nonproj_tree) == False)
    assert(is_nonproj_arc(2, nonproj_tree) == False)
    assert(is_nonproj_arc(3, nonproj_tree) == False)
    assert(is_nonproj_arc(4, nonproj_tree) == False)
    assert(is_nonproj_arc(5, nonproj_tree) == False)
    assert(is_nonproj_arc(6, nonproj_tree) == False)
    assert(is_nonproj_arc(7, nonproj_tree) == True)
    assert(is_nonproj_arc(8, nonproj_tree) == False)
    assert(is_nonproj_arc(7, partial_tree) == False)
    assert(is_nonproj_arc(17, multirooted_tree) == False)
    assert(is_nonproj_arc(16, multirooted_tree) == True)


def test_parser_is_nonproj_tree(proj_tree, nonproj_tree, partial_tree, multirooted_tree):
    assert(is_nonproj_tree(proj_tree) == False)
    assert(is_nonproj_tree(nonproj_tree) == True)
    assert(is_nonproj_tree(partial_tree) == False)
    assert(is_nonproj_tree(multirooted_tree) == True)


def test_parser_pseudoprojectivity(en_tokenizer):
    def deprojectivize(proj_heads, deco_labels):
        tokens = en_tokenizer('whatever ' * len(proj_heads))
        rel_proj_heads = [head-i for i, head in enumerate(proj_heads)]
        doc = get_doc(tokens.vocab, [t.text for t in tokens], deps=deco_labels, heads=rel_proj_heads)
        PseudoProjectivity.deprojectivize(doc)
        return [t.head.i for t in doc], [token.dep_ for token in doc]

    tree = [1, 2, 2]
    nonproj_tree = [1, 2, 2, 4, 5, 2, 7, 4, 2]
    nonproj_tree2 = [9, 1, 3, 1, 5, 6, 9, 8, 6, 1, 6, 12, 13, 10, 1]

    labels = ['det', 'nsubj', 'root', 'det', 'dobj', 'aux', 'nsubj', 'acl', 'punct']
    labels2 = ['advmod', 'root', 'det', 'nsubj', 'advmod', 'det', 'dobj', 'det', 'nmod', 'aux', 'nmod', 'advmod', 'det', 'amod', 'punct']

    assert(PseudoProjectivity.decompose('X||Y') == ('X','Y'))
    assert(PseudoProjectivity.decompose('X') == ('X',''))
    assert(PseudoProjectivity.is_decorated('X||Y') == True)
    assert(PseudoProjectivity.is_decorated('X') == False)

    PseudoProjectivity._lift(0, tree)
    assert(tree == [2, 2, 2])

    assert(PseudoProjectivity._get_smallest_nonproj_arc(nonproj_tree) == 7)
    assert(PseudoProjectivity._get_smallest_nonproj_arc(nonproj_tree2) == 10)

    proj_heads, deco_labels = PseudoProjectivity.projectivize(nonproj_tree, labels)
    assert(proj_heads == [1, 2, 2, 4, 5, 2, 7, 5, 2])
    assert(deco_labels == ['det', 'nsubj', 'root', 'det', 'dobj', 'aux',
                           'nsubj', 'acl||dobj', 'punct'])

    deproj_heads, undeco_labels = deprojectivize(proj_heads, deco_labels)
    assert(deproj_heads == nonproj_tree)
    assert(undeco_labels == labels)

    proj_heads, deco_labels = PseudoProjectivity.projectivize(nonproj_tree2, labels2)
    assert(proj_heads == [1, 1, 3, 1, 5, 6, 9, 8, 6, 1, 9, 12, 13, 10, 1])
    assert(deco_labels == ['advmod||aux', 'root', 'det', 'nsubj', 'advmod',
                           'det', 'dobj', 'det', 'nmod', 'aux', 'nmod||dobj',
                           'advmod', 'det', 'amod', 'punct'])

    deproj_heads, undeco_labels = deprojectivize(proj_heads, deco_labels)
    assert(deproj_heads == nonproj_tree2)
    assert(undeco_labels == labels2)

    # if decoration is wrong such that there is no head with the desired label
    # the structure is kept and the label is undecorated
    proj_heads = [1, 2, 2, 4, 5, 2, 7, 5, 2]
    deco_labels = ['det', 'nsubj', 'root', 'det', 'dobj', 'aux', 'nsubj',
                   'acl||iobj', 'punct']

    deproj_heads, undeco_labels = deprojectivize(proj_heads, deco_labels)
    assert(deproj_heads == proj_heads)
    assert(undeco_labels == ['det', 'nsubj', 'root', 'det', 'dobj', 'aux',
                             'nsubj', 'acl', 'punct'])

    # if there are two potential new heads, the first one is chosen even if
    # it's wrong
    proj_heads = [1, 1, 3, 1, 5, 6, 9, 8, 6, 1, 9, 12, 13, 10, 1]
    deco_labels = ['advmod||aux', 'root', 'det', 'aux', 'advmod', 'det',
                   'dobj', 'det', 'nmod', 'aux', 'nmod||dobj', 'advmod',
                   'det', 'amod', 'punct']

    deproj_heads, undeco_labels = deprojectivize(proj_heads, deco_labels)
    assert(deproj_heads == [3, 1, 3, 1, 5, 6, 9, 8, 6, 1, 6, 12, 13, 10, 1])
    assert(undeco_labels == ['advmod', 'root', 'det', 'aux', 'advmod', 'det',
                             'dobj', 'det', 'nmod', 'aux', 'nmod', 'advmod',
                             'det', 'amod', 'punct'])

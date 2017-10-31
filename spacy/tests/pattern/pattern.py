# coding: utf-8

from ..util import get_doc
from ...pattern.pattern import Tree, DependencyTree
from ...pattern.parser import PatternParser

import pytest

import logging
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


@pytest.fixture
def doc(en_vocab):
    words = ['I', "'m", 'going', 'to', 'the', 'zoo', 'next', 'week', '.']
    doc = get_doc(en_vocab,
                  words=words,
                  deps=['nsubj', 'aux', 'ROOT', 'prep', 'det', 'pobj',
                        'amod', 'npadvmod', 'punct'],
                  heads=[2, 1, 0, -1, 1, -2, 1, -5, -6])
    return doc


class TestTree:
    def test_is_connected(self):
        tree = Tree()
        tree.add_node(1)
        tree.add_node(2)
        tree.add_edge(1, 2)

        assert tree.is_connected()

        tree.add_node(3)
        assert not tree.is_connected()


class TestDependencyTree:
    def test_from_doc(self, doc):
        dep_tree = DependencyTree(doc)

        assert len(dep_tree) == len(doc)
        assert dep_tree.is_connected()
        assert dep_tree.number_of_edges() == len(doc) - 1

    def test_simple_matching(self, doc):
        dep_tree = DependencyTree(doc)
        pattern = PatternParser.parse("""root [word:going]
                                         to [word:to]
                                         [word:week]=date > root
                                         [word:/zoo|park/]=place >pobj to
                                         to >prep root
                                         """)
        assert pattern is not None
        matches = dep_tree.match(pattern)
        assert len(matches) == 1

        match = matches[0]
        assert match['place'] == doc[5]
        assert match['date'] == doc[7]

# coding: utf-8


import re
from ...pattern.parser import PatternParser


class TestPatternParser:
    def test_empty_query(self):
        assert PatternParser.parse('') is None
        assert PatternParser.parse('      ') is None

    def test_define_node(self):
        query = "fox [lemma:fox,word:fox]=alias"
        pattern = PatternParser.parse(query)

        assert pattern is not None
        assert pattern.number_of_nodes() == 1
        assert pattern.number_of_edges() == 0

        assert 'fox' in pattern.nodes

        attrs = pattern['fox']
        assert attrs.get('lemma') == 'fox'
        assert attrs.get('word') == 'fox'
        assert attrs.get('_name') == 'fox'
        assert attrs.get('_alias') == 'alias'

        for adj_list in pattern.adjacency.values():
            assert not adj_list

    def test_define_node_with_regex(self):
        query = "fox [lemma:/fo.*/]"
        pattern = PatternParser.parse(query)

        attrs = pattern['fox']
        assert attrs.get('lemma') == re.compile(r'fo.*', re.U)

    def test_define_edge(self):
        query = "[word:quick] >amod [word:fox]"
        pattern = PatternParser.parse(query)

        assert pattern is not None
        assert pattern.number_of_nodes() == 2
        assert pattern.number_of_edges() == 1

        quick_id = [node_id for node_id, node_attr in pattern.nodes.items()
                    if node_attr['word'] == 'quick'][0]

        fox_id = [node_id for node_id, node_attr in pattern.nodes.items()
                  if node_attr['word'] == 'fox'][0]

        quick_map = pattern.adjacency[quick_id]
        fox_map = pattern.adjacency[fox_id]

        assert len(quick_map) == 0
        assert len(fox_map) == 1

        dep = fox_map[quick_id]

        assert dep == 'amod'

    def test_define_edge_with_regex(self):
        query = "[word:quick] >/amod|nsubj/ [word:fox]"
        pattern = PatternParser.parse(query)

        quick_id = [node_id for node_id, node_attr in pattern.nodes.items()
                    if node_attr['word'] == 'quick'][0]

        fox_id = [node_id for node_id, node_attr in pattern.nodes.items()
                  if node_attr['word'] == 'fox'][0]

        fox_map = pattern.adjacency[fox_id]
        dep = fox_map[quick_id]

        assert dep == re.compile(r'amod|nsubj', re.U)

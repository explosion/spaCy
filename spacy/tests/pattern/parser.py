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

        base_node_id = list(pattern.adjacency.keys())[0]
        adj_map = pattern.adjacency[base_node_id]

        assert len(adj_map) == 1
        head_node_id = list(adj_map.keys())[0]
        dep = adj_map[head_node_id]

        assert dep == 'amod'
        assert pattern[base_node_id]['word'] == 'fox'
        assert pattern[head_node_id]['word'] == 'quick'

    def test_define_edge_with_regex(self):
        query = "[word:quick] >/amod|nsubj/ [word:fox]"
        pattern = PatternParser.parse(query)

        base_node_id = list(pattern.adjacency.keys())[0]
        adj_map = pattern.adjacency[base_node_id]

        assert len(adj_map) == 1
        head_node_id = list(adj_map.keys())[0]
        dep = adj_map[head_node_id]
        assert dep == re.compile(r'amod|nsubj', re.U)

# coding: utf-8

import logging
from collections import defaultdict


logger = logging.getLogger(__name__)


class Tree(object):
    def __init__(self):
        self.adjacency = defaultdict(dict)
        self.nodes = {}

    def __getitem__(self, item):
        return self.nodes[item]

    def add_node(self, node, attr_dict=None):
        attr_dict = attr_dict or {}
        self.nodes[node] = attr_dict

    def add_edge(self, u, v, dep=None):
        if u not in self.nodes or v not in self.nodes:
            raise ValueError("Each node must be defined before adding an edge.")

        self.adjacency[u][v] = dep

    def number_of_nodes(self):
        return len(self)
    
    def __len__(self):
        return len(self.nodes)

    def number_of_edges(self):
        return sum(len(adj_dict) for adj_dict in self.adjacency.values())

    def edges_iter(self, origin=None, data=True):
        nbunch = (self.adjacency.items() if origin is None
                  else [(origin, self.adjacency[origin])])

        for u, nodes in nbunch:
            for v, dep in nodes.items():
                if data:
                    yield (u, v, dep)
                else:
                    yield (u, v)
    
    def nodes_iter(self):
        for node in self.nodes.keys():
            yield node

    def is_connected(self):
        if len(self) == 0:
            raise ValueError('Connectivity is undefined for the null graph.')
        return len(set(self._plain_bfs(next(self.nodes_iter()),
                                       undirected=True))) == len(self)

    def _plain_bfs(self, source, undirected=False):
        """A fast BFS node generator.
        :param: source: the source node
        """
        seen = set()
        next_level = {source}
        while next_level:
            this_level = next_level
            next_level = set()
            for v in this_level:
                if v not in seen:
                    yield v
                    seen.add(v)
                    next_level.update(self.adjacency[v].keys())

                    if undirected:
                        for n, adj in self.adjacency.items():
                            if v in adj.keys():
                                next_level.add(n)


class DependencyPattern(Tree):
    @property
    def root_node(self):
        if self.number_of_nodes() == 1:
            # if the graph has a single node, it is the root
            return next(iter(self.nodes.keys()))

        if not self.is_connected():
            return None

        in_node = set()
        out_node = set()
        for u, v in self.edges_iter(data=False):
            in_node.add(v)
            out_node.add(u)

        try:
            return list(out_node.difference(in_node))[0]
        except IndexError:
            return None


class DependencyTree(Tree):
    def __init__(self, doc):
        super(DependencyTree, self).__init__()

        for token in doc:
            self.nodes[token.i] = token

            if token.head.i != token.i:
                # inverse the dependency to have an actual tree
                self.adjacency[token.head.i][token.i] = token.dep_

    def __getitem__(self, item):
        return self.nodes[item]

    def match_nodes(self, attr_dict, **kwargs):
        results = []
        for token_idx, token in self.nodes.items():
            if match_token(token, attr_dict, **kwargs):
                results.append(token_idx)

        return results

    def match(self, pattern):
        """Return a list of matches between the given
        :class:`DependencyPattern` and `self` if any, or None.

        :param pattern: a :class:`DependencyPattern`
        """
        pattern_root_node = pattern.root_node
        pattern_root_node_attr = pattern[pattern_root_node]
        dep_root_nodes = self.match_nodes(pattern_root_node_attr)

        if not dep_root_nodes:
            logger.debug("No node matches the pattern root "
                         "'{}'".format(pattern_root_node_attr))

        matches = []
        for candidate_root_node in dep_root_nodes:
            match_list = subtree_in_graph(candidate_root_node, self,
                                          pattern_root_node, pattern)
            for mapping in match_list:
                match = PatternMatch(mapping, pattern, self)
                matches.append(match)

        return matches


class PatternMatch(object):
    def __init__(self, mapping, pattern, tree):
        for pattern_node_id, tree_node_id in mapping.items():
            mapping[pattern_node_id] = tree[tree_node_id]
        self.mapping = mapping
        self.pattern = pattern
        self.tree = tree

        self.alias_map = {}
        for pattern_node_id in self.mapping:
            pattern_node = self.pattern[pattern_node_id]

            alias = pattern_node.get('_alias')
            if alias:
                self.alias_map[alias] = self.mapping[pattern_node_id]

    def __repr__(self):
        return "<Pattern Match: {} node>".format(len(self.mapping))

    def __getitem__(self, item):
        return self.alias_map[item]


def subtree_in_graph(dep_tree_node, dep_tree, pattern_node, pattern):
    """Return a list of matches of `pattern` as a subtree of `dep_tree`.
    :param dep_tree_node: the token (identified by its index) to start from
                          (int)
    :param dep_tree: a :class:`DependencyTree`
    :param pattern_node: the pattern node to start from
    :param pattern: a :class:`DependencyPattern`
    :return: found matches (list)
    """
    results = []
    association_dict = {pattern_node: dep_tree_node}
    _subtree_in_graph(dep_tree_node, dep_tree, pattern_node,
                      pattern, results=results,
                      association_dict=association_dict)
    results = results or []
    return results


def _subtree_in_graph(dep_tree_node, dep_tree, pattern_node, pattern,
                      association_dict=None, results=None):
    token = dep_tree[dep_tree_node]
    logger.debug("Starting from token '{}'".format(token.orth_))

    adjacent_edges = list(pattern.edges_iter(origin=pattern_node))
    if adjacent_edges:
        for (_, adjacent_pattern_node,
             dep) in adjacent_edges:
            adjacent_pattern_node_attr = pattern[adjacent_pattern_node]
            logger.debug("Exploring relation {} -[{}]-> {} from "
                         "pattern".format(pattern[pattern_node],
                                          dep,
                                          adjacent_pattern_node_attr))

            adjacent_nodes = find_adjacent_nodes(dep_tree,
                                                 dep_tree_node,
                                                 dep,
                                                 adjacent_pattern_node_attr)

            if not adjacent_nodes:
                logger.debug("No adjacent nodes in dep_tree satisfying these "
                             "conditions.")
                return None

            for adjacent_node in adjacent_nodes:
                logger.debug("Found adjacent node '{}' in "
                             "dep_tree".format(dep_tree[adjacent_node].orth_))
                association_dict[adjacent_pattern_node] = adjacent_node
                recursive_return = _subtree_in_graph(adjacent_node,
                                                     dep_tree,
                                                     adjacent_pattern_node,
                                                     pattern,
                                                     association_dict,
                                                     results=results)

                if recursive_return is None:
                    # No Match
                    return None

                association_dict, results = recursive_return

    else:
        if len(association_dict) == pattern.number_of_nodes():
            logger.debug("Add to results: {}".format(association_dict))
            results.append(dict(association_dict))

        else:
            logger.debug("{} nodes in subgraph, only {} "
                         "mapped".format(pattern.number_of_nodes(),
                                         len(association_dict)))

    logger.debug("Return intermediate: {}".format(association_dict))
    return association_dict, results


def find_adjacent_nodes(dep_tree, node, target_dep, node_attributes):
    """Find nodes adjacent to ``node`` that fulfill specified attributes
    values on edge and node.

    :param dep_tree: a :class:`DependencyTree`
    :param node: initial node to search from
    :param target_dep: edge attributes that must be fulfilled (pair-value)
     :type target_dep: dict
    :param node_attributes: node attributes that must be fulfilled (pair-value)
    :type node_attributes: dict
    :return: adjacent nodes that fulfill the given criteria (list)
    """
    results = []
    for _, adj_node, adj_dep in dep_tree.edges_iter(origin=node):
        adj_token = dep_tree[adj_node]
        if (match_edge(adj_dep, target_dep)
                and match_token(adj_token, node_attributes)):
            results.append(adj_node)

    return results


def match_edge(token_dep, target_dep):
    if target_dep is None:
        return True

    if hasattr(target_dep, 'match'):
        return target_dep.match(token_dep) is not None

    if token_dep == target_dep:
        return True

    return False


def match_token(token,
                target_attributes,
                ignore_special_key=True,
                lower=True):
    bind_map = {
        'word': lambda t: t.orth_,
        'lemma': lambda t: t.lemma_,
        'ent': lambda t: t.ent_type_,
    }

    for target_key, target_value in target_attributes.items():
        is_special_key = target_key[0] == '_'

        if ignore_special_key and is_special_key:
            continue

        if lower and hasattr(target_value, 'lower'):
            target_value = target_value.lower()

        if target_key in bind_map:
            token_attr = bind_map[target_key](token)

            if lower:
                token_attr = token_attr.lower()

            if hasattr(target_value, 'match'):  # if it is a compiled regex
                if target_value.match(token_attr) is None:
                    break
            else:
                if not token_attr == target_value:
                    break

        else:
            raise ValueError("Unknown key: '{}'".format(target_key))

    else:  # the loop was not broken
        return True

    return False

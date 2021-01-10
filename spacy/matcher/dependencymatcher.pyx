# cython: infer_types=True, profile=True
from typing import List
from collections import defaultdict

import numpy

from cymem.cymem cimport Pool

from .matcher cimport Matcher
from ..vocab cimport Vocab
from ..tokens.doc cimport Doc

from ..errors import Errors
from ..tokens import Span


DELIMITER = "||"
INDEX_HEAD = 1
INDEX_RELOP = 0


cdef class DependencyMatcher:
    """Match dependency parse tree based on pattern rules."""
    cdef Pool mem
    cdef readonly Vocab vocab
    cdef readonly Matcher matcher
    cdef public object _patterns
    cdef public object _raw_patterns
    cdef public object _keys_to_token
    cdef public object _root
    cdef public object _callbacks
    cdef public object _nodes
    cdef public object _tree
    cdef public object _ops

    def __init__(self, vocab, *, validate=False):
        """Create the DependencyMatcher.

        vocab (Vocab): The vocabulary object, which must be shared with the
            documents the matcher will operate on.
        validate (bool): Whether patterns should be validated, passed to
            Matcher as `validate`
        """
        self.matcher = Matcher(vocab, validate=validate)

        # Associates each key to the raw patterns list added by the user
        # e.g. {'key': [[{'RIGHT_ID': ..., 'RIGHT_ATTRS': ... }, ... ], ... ], ... }
        self._raw_patterns = defaultdict(list)

        # Associating each key to a list of lists of 'RIGHT_ATTRS'
        # e.g. {'key': [[{'POS': ... }, ... ], ... ], ... }
        self._patterns = defaultdict(list)

        # Associates each key to a list of dicts where each dict associates
        # a token key (used by the internal matcher) to its position within
        # the pattern
        # e.g. {'key': [ {'token_key': 2, ... }, ... ], ... }
        self._keys_to_token = defaultdict(list)

        # Associates each key to a list of ints where each int corresponds
        # to the position of the root token within the pattern
        # e.g. {'key': [3, 1, 4, ... ], ... }
        self._root = defaultdict(list)

        # Associates each key to a list of dicts where each dict associates
        # a token 'RIGHT_ID' to its position within the pattern
        # e.g. {'key': [{'right_id': 2, ...}, ... ], ...}
        self._nodes = defaultdict(list)

        # Associates each key to a list of dicts where each dict describes all
        # branches from a token (identifed by its position) to other tokens as
        # a list of tuples: ('REL_OP', 'LEFT_ID')
        # e.g. {'key': [{2: [('<', 'left_id'), ...] ...}, ... ], ...}
        self._tree = defaultdict(list)

        # Associates each key to its on_match callback
        # e.g. {'key': on_match_callback, ...}
        self._callbacks = {}

        self.vocab = vocab
        self.mem = Pool()
        self._ops = {
            "<": self.dep,
            ">": self.gov,
            "<<": self.dep_chain,
            ">>": self.gov_chain,
            ".": self.imm_precede,
            ".*": self.precede,
            ";": self.imm_follow,
            ";*": self.follow,
            "$+": self.imm_right_sib,
            "$-": self.imm_left_sib,
            "$++": self.right_sib,
            "$--": self.left_sib,
        }

    def __reduce__(self):
        data = (self.vocab, self._raw_patterns, self._callbacks)
        return (unpickle_matcher, data, None, None)

    def __len__(self):
        """Get the number of rules, which are edges, added to the dependency
        tree matcher.

        RETURNS (int): The number of rules.
        """
        return len(self._patterns)

    def __contains__(self, key):
        """Check whether the matcher contains rules for a match ID.

        key (str): The match ID.
        RETURNS (bool): Whether the matcher contains rules for this match ID.
        """
        return self.has_key(key)

    def validate_input(self, pattern, key):
        idx = 0
        visited_nodes = {}
        for relation in pattern:
            if not isinstance(relation, dict):
                raise ValueError(Errors.E1008)
            if "RIGHT_ATTRS" not in relation and "RIGHT_ID" not in relation:
                raise ValueError(Errors.E098.format(key=key))
            if idx == 0:
                if not(
                    "RIGHT_ID" in relation
                    and "REL_OP" not in relation
                    and "LEFT_ID" not in relation
                ):
                    raise ValueError(Errors.E099.format(key=key))
                visited_nodes[relation["RIGHT_ID"]] = True
            else:
                if not(
                    "RIGHT_ID" in relation
                    and "RIGHT_ATTRS" in relation
                    and "REL_OP" in relation
                    and "LEFT_ID" in relation
                ):
                    raise ValueError(Errors.E100.format(key=key))
                if (
                    relation["RIGHT_ID"] in visited_nodes
                    or relation["LEFT_ID"] not in visited_nodes
                ):
                    raise ValueError(Errors.E101.format(key=key))
                if relation["REL_OP"] not in self._ops:
                    raise ValueError(Errors.E1007.format(op=relation["REL_OP"]))
                visited_nodes[relation["RIGHT_ID"]] = True
                visited_nodes[relation["LEFT_ID"]] = True
            idx = idx + 1

    def add(self, key, patterns, *, on_match=None):
        """Add a new matcher rule to the matcher.

        key (str): The match ID.
        patterns (list): The patterns to add for the given key.
        on_match (callable): Optional callback executed on match.
        """
        if on_match is not None and not hasattr(on_match, "__call__"):
            raise ValueError(Errors.E171.format(arg_type=type(on_match)))
        if patterns is None or not isinstance(patterns, List):  # old API
            raise ValueError(Errors.E948.format(arg_type=type(patterns)))
        for pattern in patterns:
            if len(pattern) == 0:
                raise ValueError(Errors.E012.format(key=key))
            self.validate_input(pattern, key)

        key = self._normalize_key(key)

        # Save raw patterns and on_match callback
        self._raw_patterns[key].extend(patterns)
        self._callbacks[key] = on_match

        # Add 'RIGHT_ATTRS' to self._patterns[key]
        _patterns = []
        for pattern in patterns:
            token_patterns = []
            for i in range(len(pattern)):
                token_pattern = [pattern[i]["RIGHT_ATTRS"]]
                token_patterns.append(token_pattern)
            _patterns.append(token_patterns)
        self._patterns[key].extend(_patterns)

        # Add each node pattern of all the input patterns individually to the
        # matcher. This enables only a single instance of Matcher to be used.
        # Multiple adds are required to track each node pattern.
        _keys_to_token_list = []
        for i in range(len(_patterns)):
            _keys_to_token = {}
            # TODO: Better ways to hash edges in pattern?
            for j in range(len(_patterns[i])):
                k = self._normalize_key(unicode(key) + DELIMITER + unicode(i) + DELIMITER + unicode(j))
                self.matcher.add(k, [_patterns[i][j]])
                _keys_to_token[k] = j
            _keys_to_token_list.append(_keys_to_token)
        self._keys_to_token[key].extend(_keys_to_token_list)

        # Add token position to self._nodes[key][id]
        _nodes_list = []
        for pattern in patterns:
            nodes = {}
            for i in range(len(pattern)):
                nodes[pattern[i]["RIGHT_ID"]] = i
            _nodes_list.append(nodes)
        self._nodes[key].extend(_nodes_list)

        # Create an object tree to traverse later on. This data structure
        # enables easy tree pattern match. Doc-Token based tree cannot be
        # reused since it is memory-heavy and tightly coupled with the Doc.
        self._retrieve_tree(patterns, _nodes_list, key)

    def _retrieve_tree(self, patterns, _nodes_list, key):

        # List of dict of tuples
        # e.g. _heads_list = [ {token_position: [ (REL_OP, LEFT_ID), ...], ...}, ...]
        _heads_list = [] 

        # List of indices to root tokens
        _root_list = []

        # Populate _heads_list and _root_list
        for i in range(len(patterns)):
            heads = {}
            root = -1
            for j in range(len(patterns[i])):
                token_pattern = patterns[i][j]

                if "REL_OP" not in token_pattern:
                    # If 'REL_OP' is not defined, consider this the root
                    heads[j] = ('root', j)
                    root = j
                else:
                    # otherwise, we simply add a head
                    heads[j] = (
                        token_pattern["REL_OP"],
                        _nodes_list[i][token_pattern["LEFT_ID"]]
                    )
            _heads_list.append(heads)
            _root_list.append(root)

        # Group heads by left token id to create trees 
        _tree_list = []
        for i in range(len(patterns)):
            tree = defaultdict(list)
            for j in range(len(patterns[i])):
                head = _heads_list[i][j]

                # This is the root, skip it 
                if head[INDEX_HEAD] == j:
                    continue

                # Add head to tree
                tree[head[INDEX_HEAD]].append((head[INDEX_RELOP], j))

            _tree_list.append(tree)
        self._tree[key].extend(_tree_list)
        self._root[key].extend(_root_list)

    def has_key(self, key):
        """Check whether the matcher has a rule with a given key.

        key (string or int): The key to check.
        RETURNS (bool): Whether the matcher has the rule.
        """
        return self._normalize_key(key) in self._patterns

    def get(self, key, default=None):
        """Retrieve the pattern stored for a key.

        key (str / int): The key to retrieve.
        RETURNS (tuple): The rule, as an (on_match, patterns) tuple.
        """
        key = self._normalize_key(key)
        if key not in self._raw_patterns:
            return default
        return (self._callbacks[key], self._raw_patterns[key])

    def remove(self, key):
        key = self._normalize_key(key)
        if not key in self._patterns:
            raise ValueError(Errors.E175.format(key=key))
        self._patterns.pop(key)
        self._raw_patterns.pop(key)
        self._nodes.pop(key)
        self._tree.pop(key)
        self._root.pop(key)

    def __call__(self, object doclike):
        """Find all token sequences matching the supplied pattern.

        doclike (Doc or Span): The document to match over.
        RETURNS (list): A list of `(key, start, end)` tuples,
            describing the matches. A match tuple describes a span
            `doc[start:end]`. The `label_id` and `key` are both integers.
        """
        if isinstance(doclike, Doc):
            doc = doclike
        elif isinstance(doclike, Span):
            doc = doclike.as_doc()
        else:
            raise ValueError(Errors.E195.format(good="Doc or Span", got=type(doclike).__name__))
        matched_key_trees = []
        matches = self.matcher(doc)

        for key in list(self._patterns.keys()):
            _patterns_list = self._patterns[key]
            _keys_to_token_list = self._keys_to_token[key]
            _root_list = self._root[key]
            _tree_list = self._tree[key]
            _nodes_list = self._nodes[key]

            for i in range(len(_patterns_list)):
                _keys_to_token = _keys_to_token_list[i]
                _root = _root_list[i]
                _tree = _tree_list[i]
                _nodes = _nodes_list[i]

                # Creates a id_to_position dict, mapping each token id
                # to a list of positions in the doc
                # TODO: This could be taken outside to improve running time..?
                id_to_position = defaultdict(list)
                for match_id, start, end in matches:
                    if match_id in _keys_to_token:
                        id_to_position[_keys_to_token[match_id]].append(start)

                node_operator_map = self._get_node_operator_map(
                    doc,
                    _tree,
                    id_to_position,
                    _nodes,
                    _root,
                )

                matched_trees = []
                self._recurse(_tree, id_to_position, node_operator_map, 0, [], matched_trees)
                for matched_tree in matched_trees:
                    matched_key_trees.append((key, matched_tree))

            for i, (match_id, nodes) in enumerate(matched_key_trees):
                on_match = self._callbacks.get(match_id)
                if on_match is not None:
                    on_match(self, doc, i, matched_key_trees)
        return matched_key_trees

    def _recurse(self, tree, id_to_position, node_operator_map, int patternLength, visited_nodes, matched_trees):
        cdef bint isValid
        if patternLength == len(id_to_position.keys()):
            isValid = True
            for node in range(patternLength):
                if node in tree:
                    for idx, (relop,nbor) in enumerate(tree[node]):
                        computed_nbors = node_operator_map[visited_nodes[node]][relop]
                        isNbor = False
                        for computed_nbor in computed_nbors:
                            if computed_nbor.i == visited_nodes[nbor]:
                                isNbor = True
                        isValid = isValid & isNbor
            if isValid:
                matched_trees.append(visited_nodes)
            return

        for patternNode in id_to_position[patternLength]:
            self._recurse(tree, id_to_position, node_operator_map, patternLength+1, visited_nodes+[patternNode], matched_trees)

    def _get_node_operator_map(self, doc, tree, id_to_position, nodes, root):
        """
        Creates a dict of dicts which, given a node and an edge operator, contains
        the list of nodes from the doc that belong to node+operator. 
        This is used to store all the results beforehand to prevent unnecessary
        computation while pattern matching

        e.g. node_operator_map[node][operator] = [...]
        """

        all_operators = {
            child[INDEX_RELOP]
            for node in nodes.values()
            for child in tree[node]
        }

        all_nodes = {
            node_position 
            for node in nodes.values()
            for node_position in id_to_position[node]
        }

        # Create the actual node_operator_map
        node_operator_map = {}
        for node in all_nodes:
            node_operator_map[node] = {}
            for operator in all_operators:
                node_operator_map[node][operator] = self._ops[operator](doc, node)

        return node_operator_map

    def dep(self, doc, node):
        if doc[node].head == doc[node]:
            return []
        return [doc[node].head]

    def gov(self,doc,node):
        return list(doc[node].children)

    def dep_chain(self, doc, node):
        return list(doc[node].ancestors)

    def gov_chain(self, doc, node):
        return [t for t in doc[node].subtree if t != doc[node]]

    def imm_precede(self, doc, node):
        sent = self._get_sent(doc[node])
        if node < len(doc) - 1 and doc[node + 1] in sent:
            return [doc[node + 1]]
        return []

    def precede(self, doc, node):
        sent = self._get_sent(doc[node])
        return [doc[i] for i in range(node + 1, sent.end)]

    def imm_follow(self, doc, node):
        sent = self._get_sent(doc[node])
        if node > 0 and doc[node - 1] in sent:
            return [doc[node - 1]]
        return []

    def follow(self, doc, node):
        sent = self._get_sent(doc[node])
        return [doc[i] for i in range(sent.start, node)]

    def imm_right_sib(self, doc, node):
        for child in list(doc[node].head.children):
            if child.i == node + 1:
                return [doc[child.i]]
        return []

    def imm_left_sib(self, doc, node):
        for child in list(doc[node].head.children):
            if child.i == node - 1:
                return [doc[child.i]]
        return []

    def right_sib(self, doc, node):
        candidate_children = []
        for child in list(doc[node].head.children):
            if child.i > node:
                candidate_children.append(doc[child.i])
        return candidate_children

    def left_sib(self, doc, node):
        candidate_children = []
        for child in list(doc[node].head.children):
            if child.i < node:
                candidate_children.append(doc[child.i])
        return candidate_children

    def _normalize_key(self, key):
        if isinstance(key, basestring):
            return self.vocab.strings.add(key)
        else:
            return key

    def _get_sent(self, token):
        root = (list(token.ancestors) or [token])[-1]
        return token.doc[root.left_edge.i:root.right_edge.i + 1]


def unpickle_matcher(vocab, patterns, callbacks):
    matcher = DependencyMatcher(vocab)
    for key, pattern in patterns.items():
        callback = callbacks.get(key, None)
        matcher.add(key, pattern, on_match=callback)
    return matcher

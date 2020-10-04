# cython: infer_types=True, profile=True
from typing import List

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
        size = 20
        self.matcher = Matcher(vocab, validate=validate)
        self._keys_to_token = {}
        self._patterns = {}
        self._raw_patterns = {}
        self._root = {}
        self._nodes = {}
        self._tree = {}
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
        self._raw_patterns.setdefault(key, [])
        self._raw_patterns[key].extend(patterns)
        _patterns = []
        for pattern in patterns:
            token_patterns = []
            for i in range(len(pattern)):
                token_pattern = [pattern[i]["RIGHT_ATTRS"]]
                token_patterns.append(token_pattern)
            _patterns.append(token_patterns)
        self._patterns.setdefault(key, [])
        self._callbacks[key] = on_match
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
        self._keys_to_token.setdefault(key, [])
        self._keys_to_token[key].extend(_keys_to_token_list)
        _nodes_list = []
        for pattern in patterns:
            nodes = {}
            for i in range(len(pattern)):
                nodes[pattern[i]["RIGHT_ID"]] = i
            _nodes_list.append(nodes)
        self._nodes.setdefault(key, [])
        self._nodes[key].extend(_nodes_list)
        # Create an object tree to traverse later on. This data structure
        # enables easy tree pattern match. Doc-Token based tree cannot be
        # reused since it is memory-heavy and tightly coupled with the Doc.
        self.retrieve_tree(patterns, _nodes_list, key)

    def retrieve_tree(self, patterns, _nodes_list, key):
        _heads_list = []
        _root_list = []
        for i in range(len(patterns)):
            heads = {}
            root = -1
            for j in range(len(patterns[i])):
                token_pattern = patterns[i][j]
                if ("REL_OP" not in token_pattern):
                    heads[j] = ('root', j)
                    root = j
                else:
                    heads[j] = (
                        token_pattern["REL_OP"],
                        _nodes_list[i][token_pattern["LEFT_ID"]]
                    )
            _heads_list.append(heads)
            _root_list.append(root)
        _tree_list = []
        for i in range(len(patterns)):
            tree = {}
            for j in range(len(patterns[i])):
                if(_heads_list[i][j][INDEX_HEAD] == j):
                    continue
                head = _heads_list[i][j][INDEX_HEAD]
                if(head not in tree):
                    tree[head] = []
                tree[head].append((_heads_list[i][j][INDEX_RELOP], j))
            _tree_list.append(tree)
        self._tree.setdefault(key, [])
        self._tree[key].extend(_tree_list)
        self._root.setdefault(key, [])
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
            length = len(_patterns_list)
            for i in range(length):
                _keys_to_token = _keys_to_token_list[i]
                _root = _root_list[i]
                _tree = _tree_list[i]
                _nodes = _nodes_list[i]
                id_to_position = {}
                for i in range(len(_nodes)):
                    id_to_position[i]=[]
                # TODO: This could be taken outside to improve running time..?
                for match_id, start, end in matches:
                    if match_id in _keys_to_token:
                        id_to_position[_keys_to_token[match_id]].append(start)
                _node_operator_map = self.get_node_operator_map(
                    doc,
                    _tree,
                    id_to_position,
                    _nodes,_root
                )
                length = len(_nodes)

                matched_trees = []
                self.recurse(_tree, id_to_position, _node_operator_map, 0, [], matched_trees)
                for matched_tree in matched_trees:
                    matched_key_trees.append((key, matched_tree))
            for i, (match_id, nodes) in enumerate(matched_key_trees):
                on_match = self._callbacks.get(match_id)
                if on_match is not None:
                    on_match(self, doc, i, matched_key_trees)
        return matched_key_trees

    def recurse(self, tree, id_to_position, _node_operator_map, int patternLength, visited_nodes, matched_trees):
        cdef bint isValid;
        if patternLength == len(id_to_position.keys()):
            isValid = True
            for node in range(patternLength):
                if node in tree:
                    for idx, (relop,nbor) in enumerate(tree[node]):
                        computed_nbors = numpy.asarray(_node_operator_map[visited_nodes[node]][relop])
                        isNbor = False
                        for computed_nbor in computed_nbors:
                            if computed_nbor.i == visited_nodes[nbor]:
                                isNbor = True
                        isValid = isValid & isNbor
            if(isValid):
                matched_trees.append(visited_nodes)
            return
        allPatternNodes = numpy.asarray(id_to_position[patternLength])
        for patternNode in allPatternNodes:
            self.recurse(tree, id_to_position, _node_operator_map, patternLength+1, visited_nodes+[patternNode], matched_trees)

    # Given a node and an edge operator, to return the list of nodes
    # from the doc that belong to node+operator. This is used to store
    # all the results beforehand to prevent unnecessary computation while
    # pattern matching
    # _node_operator_map[node][operator] = [...]
    def get_node_operator_map(self, doc, tree, id_to_position, nodes, root):
        _node_operator_map = {}
        all_node_indices = nodes.values()
        all_operators = []
        for node in all_node_indices:
            if node in tree:
                for child in tree[node]:
                    all_operators.append(child[INDEX_RELOP])
        all_operators = list(set(all_operators))
        all_nodes = []
        for node in all_node_indices:
            all_nodes = all_nodes + id_to_position[node]
        all_nodes = list(set(all_nodes))
        for node in all_nodes:
            _node_operator_map[node] = {}
            for operator in all_operators:
                _node_operator_map[node][operator] = []
        for operator in all_operators:
            for node in all_nodes:
                _node_operator_map[node][operator] = self._ops.get(operator)(doc, node)
        return _node_operator_map

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

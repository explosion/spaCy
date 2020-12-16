# cython: infer_types=True
# cython: profile=True
from __future__ import unicode_literals

from cymem.cymem cimport Pool
from preshed.maps cimport PreshMap

from .matcher cimport Matcher
from ..vocab cimport Vocab
from ..tokens.doc cimport Doc

from .matcher import unpickle_matcher
from ..errors import Errors

from libcpp cimport bool
import numpy

DELIMITER = "||"
INDEX_HEAD = 1
INDEX_RELOP = 0


cdef class DependencyMatcher:
    """Match dependency parse tree based on pattern rules."""
    cdef Pool mem
    cdef readonly Vocab vocab
    cdef readonly Matcher token_matcher
    cdef public object _patterns
    cdef public object _keys_to_token
    cdef public object _root
    cdef public object _entities
    cdef public object _callbacks
    cdef public object _nodes
    cdef public object _tree

    def __init__(self, vocab):
        """Create the DependencyMatcher.

        vocab (Vocab): The vocabulary object, which must be shared with the
            documents the matcher will operate on.
        RETURNS (DependencyMatcher): The newly constructed object.
        """
        size = 20
        self.token_matcher = Matcher(vocab)
        self._keys_to_token = {}
        self._patterns = {}
        self._root = {}
        self._nodes = {}
        self._tree = {}
        self._entities = {}
        self._callbacks = {}
        self.vocab = vocab
        self.mem = Pool()

    def __reduce__(self):
        data = (self.vocab, self._patterns,self._tree, self._callbacks)
        return (unpickle_matcher, data, None, None)

    def __len__(self):
        """Get the number of rules, which are edges, added to the dependency
        tree matcher.

        RETURNS (int): The number of rules.
        """
        return len(self._patterns)

    def __contains__(self, key):
        """Check whether the matcher contains rules for a match ID.

        key (unicode): The match ID.
        RETURNS (bool): Whether the matcher contains rules for this match ID.
        """
        return self._normalize_key(key) in self._patterns

    def validateInput(self, pattern, key):
        idx = 0
        visitedNodes = {}
        for relation in pattern:
            if "PATTERN" not in relation or "SPEC" not in relation:
                raise ValueError(Errors.E098.format(key=key))
            if idx == 0:
                if not(
                    "NODE_NAME" in relation["SPEC"]
                    and "NBOR_RELOP" not in relation["SPEC"]
                    and "NBOR_NAME" not in relation["SPEC"]
                ):
                    raise ValueError(Errors.E099.format(key=key))
                visitedNodes[relation["SPEC"]["NODE_NAME"]] = True
            else:
                if not(
                    "NODE_NAME" in relation["SPEC"]
                    and "NBOR_RELOP" in relation["SPEC"]
                    and "NBOR_NAME" in relation["SPEC"]
                ):
                    raise ValueError(Errors.E100.format(key=key))
                if (
                    relation["SPEC"]["NODE_NAME"] in visitedNodes
                    or relation["SPEC"]["NBOR_NAME"] not in visitedNodes
                ):
                    raise ValueError(Errors.E101.format(key=key))
                visitedNodes[relation["SPEC"]["NODE_NAME"]] = True
                visitedNodes[relation["SPEC"]["NBOR_NAME"]] = True
            idx = idx + 1

    def add(self, key, patterns, *_patterns, on_match=None):
        if patterns is None or hasattr(patterns, "__call__"):  # old API
            on_match = patterns
            patterns = _patterns
        for pattern in patterns:
            if len(pattern) == 0:
                raise ValueError(Errors.E012.format(key=key))
            self.validateInput(pattern,key)
        key = self._normalize_key(key)
        _patterns = []
        for pattern in patterns:
            token_patterns = []
            for i in range(len(pattern)):
                token_pattern = [pattern[i]["PATTERN"]]
                token_patterns.append(token_pattern)
            # self.patterns.append(token_patterns)
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
                self.token_matcher.add(k, None, _patterns[i][j])
                _keys_to_token[k] = j
            _keys_to_token_list.append(_keys_to_token)
        self._keys_to_token.setdefault(key, [])
        self._keys_to_token[key].extend(_keys_to_token_list)
        _nodes_list = []
        for pattern in patterns:
            nodes = {}
            for i in range(len(pattern)):
                nodes[pattern[i]["SPEC"]["NODE_NAME"]] = i
            _nodes_list.append(nodes)
        self._nodes.setdefault(key, [])
        self._nodes[key].extend(_nodes_list)
        # Create an object tree to traverse later on. This data structure
        # enables easy tree pattern match. Doc-Token based tree cannot be
        # reused since it is memory-heavy and tightly coupled with the Doc.
        self.retrieve_tree(patterns, _nodes_list,key)

    def retrieve_tree(self, patterns, _nodes_list, key):
        _heads_list = []
        _root_list = []
        for i in range(len(patterns)):
            heads = {}
            root = -1
            for j in range(len(patterns[i])):
                token_pattern = patterns[i][j]
                if ("NBOR_RELOP" not in token_pattern["SPEC"]):
                    heads[j] = ('root', j)
                    root = j
                else:
                    heads[j] = (
                        token_pattern["SPEC"]["NBOR_RELOP"],
                        _nodes_list[i][token_pattern["SPEC"]["NBOR_NAME"]]
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
        key = self._normalize_key(key)
        return key in self._patterns

    def get(self, key, default=None):
        """Retrieve the pattern stored for a key.

        key (unicode or int): The key to retrieve.
        RETURNS (tuple): The rule, as an (on_match, patterns) tuple.
        """
        key = self._normalize_key(key)
        if key not in self._patterns:
            return default
        return (self._callbacks[key], self._patterns[key])

    def __call__(self, Doc doc):
        matched_key_trees = []
        matches = self.token_matcher(doc)
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
                self.recurse(_tree,id_to_position,_node_operator_map,0,[],matched_trees)
                if len(matched_trees) > 0:
                    matched_key_trees.append((key,matched_trees))
        for i, (ent_id, nodes) in enumerate(matched_key_trees):
            on_match = self._callbacks.get(ent_id)
            if on_match is not None:
                on_match(self, doc, i, matched_key_trees)
        return matched_key_trees

    def recurse(self,tree,id_to_position,_node_operator_map,int patternLength,visitedNodes,matched_trees):
        cdef bool isValid;
        if(patternLength == len(id_to_position.keys())):
            isValid = True
            for node in range(patternLength):
                if(node in tree):
                    for idx, (relop,nbor) in enumerate(tree[node]):
                        computed_nbors = numpy.asarray(_node_operator_map[visitedNodes[node]][relop])
                        isNbor = False
                        for computed_nbor in computed_nbors:
                            if(computed_nbor.i == visitedNodes[nbor]):
                                isNbor = True
                        isValid = isValid & isNbor
            if(isValid):
                matched_trees.append(visitedNodes)
            return
        allPatternNodes = numpy.asarray(id_to_position[patternLength])
        for patternNode in allPatternNodes:
            self.recurse(tree,id_to_position,_node_operator_map,patternLength+1,visitedNodes+[patternNode],matched_trees)

    # Given a node and an edge operator, to return the list of nodes
    # from the doc that belong to node+operator. This is used to store
    # all the results beforehand to prevent unnecessary computation while
    # pattern matching
    # _node_operator_map[node][operator] = [...]
    def get_node_operator_map(self,doc,tree,id_to_position,nodes,root):
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
        # Used to invoke methods for each operator
        switcher = {
            "<": self.dep,
            ">": self.gov,
            "<<": self.dep_chain,
            ">>": self.gov_chain,
            ".": self.imm_precede,
            "$+": self.imm_right_sib,
            "$-": self.imm_left_sib,
            "$++": self.right_sib,
            "$--": self.left_sib
        }
        for operator in all_operators:
            for node in all_nodes:
                _node_operator_map[node][operator] = switcher.get(operator)(doc,node)
        return _node_operator_map

    def dep(self, doc, node):
        return [doc[node].head]

    def gov(self,doc,node):
        return list(doc[node].children)

    def dep_chain(self, doc, node):
        return list(doc[node].ancestors)

    def gov_chain(self, doc, node):
        return list(doc[node].subtree)

    def imm_precede(self, doc, node):
        if node > 0:
            return [doc[node - 1]]
        return []

    def imm_right_sib(self, doc, node):
        for child in list(doc[node].head.children):
            if child.i == node - 1:
                return [doc[child.i]]
        return []

    def imm_left_sib(self, doc, node):
        for child in list(doc[node].head.children):
            if child.i == node + 1:
                return [doc[child.i]]
        return []

    def right_sib(self, doc, node):
        candidate_children = []
        for child in list(doc[node].head.children):
            if child.i < node:
                candidate_children.append(doc[child.i])
        return candidate_children

    def left_sib(self, doc, node):
        candidate_children = []
        for child in list(doc[node].head.children):
            if child.i > node:
                candidate_children.append(doc[child.i])
        return candidate_children

    def _normalize_key(self, key):
        if isinstance(key, basestring):
            return self.vocab.strings.add(key)
        else:
            return key

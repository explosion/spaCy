# cython: profile=True
# cython: infer_types=True
# coding: utf8
from __future__ import unicode_literals

import ujson
from cymem.cymem cimport Pool
from preshed.maps cimport PreshMap
from libcpp.vector cimport vector
from libcpp.pair cimport pair
from murmurhash.mrmr cimport hash64
from libc.stdint cimport int32_t

from .typedefs cimport attr_t
from .typedefs cimport hash_t
from .structs cimport TokenC
from .tokens.doc cimport Doc, get_token_attr
from .vocab cimport Vocab
from .errors import Errors, TempErrors

from .attrs import IDS
from .attrs cimport attr_id_t, ID, NULL_ATTR
from .attrs import FLAG61 as U_ENT
from .attrs import FLAG60 as B2_ENT
from .attrs import FLAG59 as B3_ENT
from .attrs import FLAG58 as B4_ENT
from .attrs import FLAG57 as B5_ENT
from .attrs import FLAG56 as B6_ENT
from .attrs import FLAG55 as B7_ENT
from .attrs import FLAG54 as B8_ENT
from .attrs import FLAG53 as B9_ENT
from .attrs import FLAG52 as B10_ENT
from .attrs import FLAG51 as I3_ENT
from .attrs import FLAG50 as I4_ENT
from .attrs import FLAG49 as I5_ENT
from .attrs import FLAG48 as I6_ENT
from .attrs import FLAG47 as I7_ENT
from .attrs import FLAG46 as I8_ENT
from .attrs import FLAG45 as I9_ENT
from .attrs import FLAG44 as I10_ENT
from .attrs import FLAG43 as L2_ENT
from .attrs import FLAG42 as L3_ENT
from .attrs import FLAG41 as L4_ENT
from .attrs import FLAG40 as L5_ENT
from .attrs import FLAG39 as L6_ENT
from .attrs import FLAG38 as L7_ENT
from .attrs import FLAG37 as L8_ENT
from .attrs import FLAG36 as L9_ENT
from .attrs import FLAG35 as L10_ENT

DELIMITER = '||'

cpdef enum quantifier_t:
    _META
    ONE
    ZERO
    ZERO_ONE
    ZERO_PLUS


cdef enum action_t:
    REJECT
    ADVANCE
    REPEAT
    ACCEPT
    ADVANCE_ZERO
    ACCEPT_PREV
    PANIC

# A "match expression" consists of one or more token patterns
# Each token pattern consists of a quantifier and 0+ (attr, value) pairs.
# A state is an (int, pattern pointer) pair, where the int is the start
# position, and the pattern pointer shows where we're up to
# in the pattern.

cdef struct AttrValueC:
    attr_id_t attr
    attr_t value

cdef struct TokenPatternC:
    AttrValueC* attrs
    int32_t nr_attr
    quantifier_t quantifier

ctypedef TokenPatternC* TokenPatternC_ptr
ctypedef pair[int, TokenPatternC_ptr] StateC

DEF PADDING = 5


cdef TokenPatternC* init_pattern(Pool mem, attr_t entity_id,
                                 object token_specs) except NULL:
    pattern = <TokenPatternC*>mem.alloc(len(token_specs) + 1, sizeof(TokenPatternC))
    cdef int i
    for i, (quantifier, spec) in enumerate(token_specs):
        pattern[i].quantifier = quantifier
        pattern[i].attrs = <AttrValueC*>mem.alloc(len(spec), sizeof(AttrValueC))
        pattern[i].nr_attr = len(spec)
        for j, (attr, value) in enumerate(spec):
            pattern[i].attrs[j].attr = attr
            pattern[i].attrs[j].value = value
    i = len(token_specs)
    pattern[i].attrs = <AttrValueC*>mem.alloc(2, sizeof(AttrValueC))
    pattern[i].attrs[0].attr = ID
    pattern[i].attrs[0].value = entity_id
    pattern[i].nr_attr = 0
    return pattern

cdef attr_t get_pattern_key(const TokenPatternC* pattern) except 0:
    while pattern.nr_attr != 0:
        pattern += 1
    id_attr = pattern[0].attrs[0]
    if id_attr.attr != ID:
        raise ValueError(Errors.E074.format(attr=ID, bad_attr=id_attr.attr))
    return id_attr.value


cdef int get_action(const TokenPatternC* pattern, const TokenC* token) nogil:
    lookahead = &pattern[1]
    for attr in pattern.attrs[:pattern.nr_attr]:
        if get_token_attr(token, attr.attr) != attr.value:
            if pattern.quantifier == ONE:
                return REJECT
            elif pattern.quantifier == ZERO:
                return ACCEPT if lookahead.nr_attr == 0 else ADVANCE
            elif pattern.quantifier in (ZERO_ONE, ZERO_PLUS):
                return ACCEPT_PREV if lookahead.nr_attr == 0 else ADVANCE_ZERO
            else:
                return PANIC
    if pattern.quantifier == ZERO:
        return REJECT
    elif lookahead.nr_attr == 0:
        return ACCEPT
    elif pattern.quantifier in (ONE, ZERO_ONE):
        return ADVANCE
    elif pattern.quantifier == ZERO_PLUS:
        # This is a bandaid over the 'shadowing' problem described here:
        # https://github.com/explosion/spaCy/issues/864
        next_action = get_action(lookahead, token)
        if next_action is REJECT:
            return REPEAT
        else:
            return ADVANCE_ZERO
    else:
        return PANIC


def _convert_strings(token_specs, string_store):
    # Support 'syntactic sugar' operator '+', as combination of ONE, ZERO_PLUS
    operators = {'!': (ZERO,), '*': (ZERO_PLUS,), '+': (ONE, ZERO_PLUS),
                 '?': (ZERO_ONE,), '1': (ONE,)}
    tokens = []
    op = ONE
    for spec in token_specs:
        if not spec:
            # Signifier for 'any token'
            tokens.append((ONE, [(NULL_ATTR, 0)]))
            continue
        token = []
        ops = (ONE,)
        for attr, value in spec.items():
            if isinstance(attr, basestring) and attr.upper() == 'OP':
                if value in operators:
                    ops = operators[value]
                else:
                    keys = ', '.join(operators.keys())
                    raise KeyError(Errors.E011.format(op=value, opts=keys))
            if isinstance(attr, basestring):
                attr = IDS.get(attr.upper())
            if isinstance(value, basestring):
                value = string_store.add(value)
            if isinstance(value, bool):
                value = int(value)
            if attr is not None:
                token.append((attr, value))
        for op in ops:
            tokens.append((op, token))
    return tokens


def merge_phrase(matcher, doc, i, matches):
    """Callback to merge a phrase on match."""
    ent_id, label, start, end = matches[i]
    span = doc[start:end]
    span.merge(ent_type=label, ent_id=ent_id)


def unpickle_matcher(vocab, patterns, callbacks):
    matcher = Matcher(vocab)
    for key, specs in patterns.items():
        callback = callbacks.get(key, None)
        matcher.add(key, callback, *specs)
    return matcher


cdef class Matcher:
    """Match sequences of tokens, based on pattern rules."""
    cdef Pool mem
    cdef vector[TokenPatternC*] patterns
    cdef readonly Vocab vocab
    cdef public object _patterns
    cdef public object _entities
    cdef public object _callbacks

    def __init__(self, vocab):
        """Create the Matcher.

        vocab (Vocab): The vocabulary object, which must be shared with the
            documents the matcher will operate on.
        RETURNS (Matcher): The newly constructed object.
        """
        self._patterns = {}
        self._entities = {}
        self._callbacks = {}
        self.vocab = vocab
        self.mem = Pool()

    def __reduce__(self):
        data = (self.vocab, self._patterns, self._callbacks)
        return (unpickle_matcher, data, None, None)

    def __len__(self):
        """Get the number of rules added to the matcher. Note that this only
        returns the number of rules (identical with the number of IDs), not the
        number of individual patterns.

        RETURNS (int): The number of rules.
        """
        return len(self._patterns)

    def __contains__(self, key):
        """Check whether the matcher contains rules for a match ID.

        key (unicode): The match ID.
        RETURNS (bool): Whether the matcher contains rules for this match ID.
        """
        return self._normalize_key(key) in self._patterns

    def add(self, key, on_match, *patterns):
        """Add a match-rule to the matcher. A match-rule consists of: an ID
        key, an on_match callback, and one or more patterns.

        If the key exists, the patterns are appended to the previous ones, and
        the previous on_match callback is replaced. The `on_match` callback
        will receive the arguments `(matcher, doc, i, matches)`. You can also
        set `on_match` to `None` to not perform any actions.

        A pattern consists of one or more `token_specs`, where a `token_spec`
        is a dictionary mapping attribute IDs to values, and optionally a
        quantifier operator under the key "op". The available quantifiers are:

        '!': Negate the pattern, by requiring it to match exactly 0 times.
        '?': Make the pattern optional, by allowing it to match 0 or 1 times.
        '+': Require the pattern to match 1 or more times.
        '*': Allow the pattern to zero or more times.

        The + and * operators are usually interpretted "greedily", i.e. longer
        matches are returned where possible. However, if you specify two '+'
        and '*' patterns in a row and their matches overlap, the first
        operator will behave non-greedily. This quirk in the semantics makes
        the matcher more efficient, by avoiding the need for back-tracking.

        key (unicode): The match ID.
        on_match (callable): Callback executed on match.
        *patterns (list): List of token descriptions.
        """
        for pattern in patterns:
            if len(pattern) == 0:
                raise ValueError(Errors.E012.format(key=key))
        key = self._normalize_key(key)
        for pattern in patterns:
            specs = _convert_strings(pattern, self.vocab.strings)
            self.patterns.push_back(init_pattern(self.mem, key, specs))
        self._patterns.setdefault(key, [])
        self._callbacks[key] = on_match
        self._patterns[key].extend(patterns)

    def remove(self, key):
        """Remove a rule from the matcher. A KeyError is raised if the key does
        not exist.

        key (unicode): The ID of the match rule.
        """
        key = self._normalize_key(key)
        self._patterns.pop(key)
        self._callbacks.pop(key)
        cdef int i = 0
        while i < self.patterns.size():
            pattern_key = get_pattern_key(self.patterns.at(i))
            if pattern_key == key:
                self.patterns.erase(self.patterns.begin()+i)
            else:
                i += 1

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

    def pipe(self, docs, batch_size=1000, n_threads=2):
        """Match a stream of documents, yielding them in turn.

        docs (iterable): A stream of documents.
        batch_size (int): Number of documents to accumulate into a working set.
        n_threads (int): The number of threads with which to work on the buffer
            in parallel, if the implementation supports multi-threading.
        YIELDS (Doc): Documents, in order.
        """
        for doc in docs:
            self(doc)
            yield doc

    def __call__(self, Doc doc):
        """Find all token sequences matching the supplied pattern.

        doc (Doc): The document to match over.
        RETURNS (list): A list of `(key, start, end)` tuples,
            describing the matches. A match tuple describes a span
            `doc[start:end]`. The `label_id` and `key` are both integers.
        """
        cdef vector[StateC] partials
        cdef int n_partials = 0
        cdef int q = 0
        cdef int i, token_i
        cdef const TokenC* token
        cdef StateC state
        matches = []
        for token_i in range(doc.length):
            token = &doc.c[token_i]
            q = 0
            # Go over the open matches, extending or finalizing if able.
            # Otherwise, we over-write them (q doesn't advance)
            for state in partials:
                action = get_action(state.second, token)
                if action == PANIC:
                    raise ValueError(Errors.E013)
                while action == ADVANCE_ZERO:
                    state.second += 1
                    action = get_action(state.second, token)
                if action == PANIC:
                    raise ValueError(Errors.E013)
                if action == REPEAT:
                    # Leave the state in the queue, and advance to next slot
                    # (i.e. we don't overwrite -- we want to greedily match
                    # more pattern.
                    q += 1
                elif action == REJECT:
                    pass
                elif action == ADVANCE:
                    partials[q] = state
                    partials[q].second += 1
                    q += 1
                elif action in (ACCEPT, ACCEPT_PREV):
                    # TODO: What to do about patterns starting with ZERO? Need
                    # to adjust the start position.
                    start = state.first
                    end = token_i+1 if action == ACCEPT else token_i
                    ent_id = state.second[1].attrs[0].value
                    label = state.second[1].attrs[1].value
                    matches.append((ent_id, start, end))

            partials.resize(q)
            # Check whether we open any new patterns on this token
            for pattern in self.patterns:
                action = get_action(pattern, token)
                if action == PANIC:
                    raise ValueError(Errors.E013)
                while action == ADVANCE_ZERO:
                    pattern += 1
                    action = get_action(pattern, token)
                if action == REPEAT:
                    state.first = token_i
                    state.second = pattern
                    partials.push_back(state)
                elif action == ADVANCE:
                    # TODO: What to do about patterns starting with ZERO? Need
                    # to adjust the start position.
                    state.first = token_i
                    state.second = pattern + 1
                    partials.push_back(state)
                elif action in (ACCEPT, ACCEPT_PREV):
                    start = token_i
                    end = token_i+1 if action == ACCEPT else token_i
                    ent_id = pattern[1].attrs[0].value
                    label = pattern[1].attrs[1].value
                    matches.append((ent_id, start, end))
        # Look for open patterns that are actually satisfied
        for state in partials:
            while state.second.quantifier in (ZERO, ZERO_ONE, ZERO_PLUS):
                state.second += 1
                if state.second.nr_attr == 0:
                    start = state.first
                    end = len(doc)
                    ent_id = state.second.attrs[0].value
                    label = state.second.attrs[0].value
                    matches.append((ent_id, start, end))
        for i, (ent_id, start, end) in enumerate(matches):
            on_match = self._callbacks.get(ent_id)
            if on_match is not None:
                on_match(self, doc, i, matches)
        return matches

    def _normalize_key(self, key):
        if isinstance(key, basestring):
            return self.vocab.strings.add(key)
        else:
            return key


def get_bilou(length):
    if length == 1:
        return [U_ENT]
    elif length == 2:
        return [B2_ENT, L2_ENT]
    elif length == 3:
        return [B3_ENT, I3_ENT, L3_ENT]
    elif length == 4:
        return [B4_ENT, I4_ENT, I4_ENT, L4_ENT]
    elif length == 5:
        return [B5_ENT, I5_ENT, I5_ENT, I5_ENT, L5_ENT]
    elif length == 6:
        return [B6_ENT, I6_ENT, I6_ENT, I6_ENT, I6_ENT, L6_ENT]
    elif length == 7:
        return [B7_ENT, I7_ENT, I7_ENT, I7_ENT, I7_ENT, I7_ENT, L7_ENT]
    elif length == 8:
        return [B8_ENT, I8_ENT, I8_ENT, I8_ENT, I8_ENT, I8_ENT, I8_ENT, L8_ENT]
    elif length == 9:
        return [B9_ENT, I9_ENT, I9_ENT, I9_ENT, I9_ENT, I9_ENT, I9_ENT, I9_ENT,
                L9_ENT]
    elif length == 10:
        return [B10_ENT, I10_ENT, I10_ENT, I10_ENT, I10_ENT, I10_ENT, I10_ENT,
                I10_ENT, I10_ENT, L10_ENT]
    else:
        raise ValueError(TempErrors.T001)


cdef class PhraseMatcher:
    cdef Pool mem
    cdef Vocab vocab
    cdef Matcher matcher
    cdef PreshMap phrase_ids
    cdef int max_length
    cdef attr_t* _phrase_key
    cdef public object _callbacks
    cdef public object _patterns

    def __init__(self, Vocab vocab, max_length=10):
        self.mem = Pool()
        self._phrase_key = <attr_t*>self.mem.alloc(max_length, sizeof(attr_t))
        self.max_length = max_length
        self.vocab = vocab
        self.matcher = Matcher(self.vocab)
        self.phrase_ids = PreshMap()
        abstract_patterns = []
        for length in range(1, max_length):
            abstract_patterns.append([{tag: True}
                                      for tag in get_bilou(length)])
        self.matcher.add('Candidate', None, *abstract_patterns)
        self._callbacks = {}

    def __len__(self):
        """Get the number of rules added to the matcher. Note that this only
        returns the number of rules (identical with the number of IDs), not the
        number of individual patterns.

        RETURNS (int): The number of rules.
        """
        return len(self.phrase_ids)

    def __contains__(self, key):
        """Check whether the matcher contains rules for a match ID.

        key (unicode): The match ID.
        RETURNS (bool): Whether the matcher contains rules for this match ID.
        """
        cdef hash_t ent_id = self.matcher._normalize_key(key)
        return ent_id in self._callbacks

    def __reduce__(self):
        return (self.__class__, (self.vocab,), None, None)

    def add(self, key, on_match, *docs):
        """Add a match-rule to the matcher. A match-rule consists of: an ID
        key, an on_match callback, and one or more patterns.

        key (unicode): The match ID.
        on_match (callable): Callback executed on match.
        *docs (Doc): `Doc` objects representing match patterns.
        """
        cdef Doc doc
        for doc in docs:
            if len(doc) >= self.max_length:
                raise ValueError(TempErrors.T002.format(doc_len=len(doc),
                                                        max_len=self.max_length))
        cdef hash_t ent_id = self.matcher._normalize_key(key)
        self._callbacks[ent_id] = on_match
        cdef int length
        cdef int i
        cdef hash_t phrase_hash
        for doc in docs:
            length = doc.length
            tags = get_bilou(length)
            for i in range(self.max_length):
                self._phrase_key[i] = 0
            for i, tag in enumerate(tags):
                lexeme = self.vocab[doc.c[i].lex.orth]
                lexeme.set_flag(tag, True)
                self._phrase_key[i] = lexeme.orth
            phrase_hash = hash64(self._phrase_key,
                                 self.max_length * sizeof(attr_t), 0)
            self.phrase_ids.set(phrase_hash, <void*>ent_id)

    def __call__(self, Doc doc):

        """Find all sequences matching the supplied patterns on the `Doc`.

        doc (Doc): The document to match over.
        RETURNS (list): A list of `(key, start, end)` tuples,
            describing the matches. A match tuple describes a span
            `doc[start:end]`. The `label_id` and `key` are both integers.
        """
        matches = []
        for _, start, end in self.matcher(doc):
            ent_id = self.accept_match(doc, start, end)
            if ent_id is not None:
                matches.append((ent_id, start, end))
        for i, (ent_id, start, end) in enumerate(matches):
            on_match = self._callbacks.get(ent_id)
            if on_match is not None:
                on_match(self, doc, i, matches)
        return matches

    def pipe(self, stream, batch_size=1000, n_threads=2):
        """Match a stream of documents, yielding them in turn.

        docs (iterable): A stream of documents.
        batch_size (int): Number of documents to accumulate into a working set.
        n_threads (int): The number of threads with which to work on the buffer
            in parallel, if the implementation supports multi-threading.
        YIELDS (Doc): Documents, in order.
        """
        for doc in stream:
            self(doc)
            yield doc

    def accept_match(self, Doc doc, int start, int end):
        if (end - start) >= self.max_length:
            raise ValueError(Errors.E075.format(length=end - start,
                                                max_len=self.max_length))
        cdef int i, j
        for i in range(self.max_length):
            self._phrase_key[i] = 0
        for i, j in enumerate(range(start, end)):
            self._phrase_key[i] = doc.c[j].lex.orth
        cdef hash_t key = hash64(self._phrase_key,
                                 self.max_length * sizeof(attr_t), 0)
        ent_id = <hash_t>self.phrase_ids.get(key)
        if ent_id == 0:
            return None
        else:
            return ent_id

cdef class DependencyTreeMatcher:
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
        """Create the DependencyTreeMatcher.

        vocab (Vocab): The vocabulary object, which must be shared with the
            documents the matcher will operate on.
        RETURNS (DependencyTreeMatcher): The newly constructed object.
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
        """Get the number of rules, which are edges ,added to the dependency tree matcher.

        RETURNS (int): The number of rules.
        """
        return len(self._patterns)

    def __contains__(self, key):
        """Check whether the matcher contains rules for a match ID.

        key (unicode): The match ID.
        RETURNS (bool): Whether the matcher contains rules for this match ID.
        """
        return self._normalize_key(key) in self._patterns


    def add(self, key, on_match, *patterns):

        # TODO : validations
        # 1. check if input pattern is connected
        # 2. check if pattern format is correct
        # 3. check if atleast one root node is present
        # 4. check if node names are not repeated
        # 5. check if each node has only one head

        for pattern in patterns:
            if len(pattern) == 0:
                raise ValueError(Errors.E012.format(key=key))

        key = self._normalize_key(key)

        _patterns = []
        for pattern in patterns:
            token_patterns = []
            for i in range(len(pattern)):
                token_pattern = [pattern[i]['PATTERN']]
                token_patterns.append(token_pattern)
            # self.patterns.append(token_patterns)
            _patterns.append(token_patterns)

        self._patterns.setdefault(key, [])
        self._callbacks[key] = on_match
        self._patterns[key].extend(_patterns)

        # Add each node pattern of all the input patterns individually to the matcher.
        # This enables only a single instance of Matcher to be used.
        # Multiple adds are required to track each node pattern.
        _keys_to_token_list = []
        for i in range(len(_patterns)):
            _keys_to_token = {}
            # TODO : Better ways to hash edges in pattern?
            for j in range(len(_patterns[i])):
                k = self._normalize_key(unicode(key)+DELIMITER+unicode(i)+DELIMITER+unicode(j))
                self.token_matcher.add(k,None,_patterns[i][j])
                _keys_to_token[k] = j
            _keys_to_token_list.append(_keys_to_token)

        self._keys_to_token.setdefault(key, [])
        self._keys_to_token[key].extend(_keys_to_token_list)

        _nodes_list = []
        for pattern in patterns:
            nodes = {}
            for i in range(len(pattern)):
                nodes[pattern[i]['SPEC']['NODE_NAME']]=i
            _nodes_list.append(nodes)

        self._nodes.setdefault(key, [])
        self._nodes[key].extend(_nodes_list)

        # Create an object tree to traverse later on.
        # This datastructure enable easy tree pattern match.
        # Doc-Token based tree cannot be reused since it is memory heavy and tightly coupled with doc
        self.retrieve_tree(patterns,_nodes_list,key)

    def retrieve_tree(self,patterns,_nodes_list,key):

        _heads_list = []
        _root_list = []
        for i in range(len(patterns)):
            heads = {}
            root = -1
            for j in range(len(patterns[i])):
                token_pattern = patterns[i][j]
                if('NBOR_RELOP' not in token_pattern['SPEC']):
                    heads[j] = j
                    root = j
                else:
                    # TODO: Add semgrex rules
                    # 1. >
                    if(token_pattern['SPEC']['NBOR_RELOP'] == '>'):
                        heads[j] = _nodes_list[i][token_pattern['SPEC']['NBOR_NAME']]
                    # 2. <
                    if(token_pattern['SPEC']['NBOR_RELOP'] == '<'):
                        heads[_nodes_list[i][token_pattern['SPEC']['NBOR_NAME']]] = j

            _heads_list.append(heads)
            _root_list.append(root)

        _tree_list = []
        for i in range(len(patterns)):
            tree = {}
            for j in range(len(patterns[i])):
                if(j == _heads_list[i][j]):
                    continue
                head = _heads_list[i][j]
                if(head not in tree):
                    tree[head] = []
                tree[head].append(j)
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
        matched_trees = []

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

                # This could be taken outside to improve running time..?
                for match_id, start, end in matches:
                    if match_id in _keys_to_token:
                        if _keys_to_token[match_id] not in id_to_position:
                            id_to_position[_keys_to_token[match_id]] = []
                        id_to_position[_keys_to_token[match_id]].append(start)

                length = len(_nodes)
                if _root in id_to_position:
                    candidates = id_to_position[_root]
                    for candidate in candidates:
                        isVisited = {}
                        self.dfs(candidate,_root,_tree,id_to_position,doc,isVisited)
                        # to check if the subtree pattern is completely identified
                        if(len(isVisited) == length):
                            matched_trees.append((key,list(isVisited)))

            for i, (ent_id, nodes) in enumerate(matched_trees):
                on_match = self._callbacks.get(ent_id)
                if on_match is not None:
                    on_match(self, doc, i, matches)

        return matched_trees

    def dfs(self,candidate,root,tree,id_to_position,doc,isVisited):
        if(root in id_to_position and candidate in id_to_position[root]):
            # color the node since it is valid
            isVisited[candidate] = True
            candidate_children = doc[candidate].children
            for candidate_child in candidate_children:
                if root in tree:
                    for root_child in tree[root]:
                        self.dfs(candidate_child.i,root_child,tree,id_to_position,doc,isVisited)


    def _normalize_key(self, key):
        if isinstance(key, basestring):
            return self.vocab.strings.add(key)
        else:
            return key
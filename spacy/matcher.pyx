# cython: infer_types=True
# cython: profile=True
from __future__ import unicode_literals
from libcpp.vector cimport vector
from libc.stdint cimport int32_t, uint64_t, uint16_t
from preshed.maps cimport PreshMap
from cymem.cymem cimport Pool
from murmurhash.mrmr cimport hash64
from .typedefs cimport attr_t, hash_t
from .structs cimport TokenC
from .lexeme cimport attr_id_t
from .vocab cimport Vocab
from .tokens.doc cimport Doc
from .tokens.doc cimport get_token_attr
from .attrs cimport ID, attr_id_t, NULL_ATTR, ORTH
from .errors import Errors, TempErrors, Warnings, deprecation_warning

from .attrs import IDS
from .attrs import FLAG61 as U_ENT
from .attrs import FLAG60 as B2_ENT
from .attrs import FLAG59 as B3_ENT
from .attrs import FLAG58 as B4_ENT
from .attrs import FLAG43 as L2_ENT
from .attrs import FLAG42 as L3_ENT
from .attrs import FLAG41 as L4_ENT
from .attrs import FLAG43 as I2_ENT
from .attrs import FLAG42 as I3_ENT
from .attrs import FLAG41 as I4_ENT

DELIMITER = '||'

DELIMITER = '||'
INDEX_HEAD = 1
INDEX_RELOP = 0

cdef enum action_t:
    REJECT = 0000
    MATCH = 1000
    ADVANCE = 0100
    RETRY = 0010
    RETRY_EXTEND = 0011
    MATCH_EXTEND = 1001
    MATCH_REJECT = 2000


cdef enum quantifier_t:
    ZERO
    ZERO_ONE
    ZERO_PLUS
    ONE
    ONE_PLUS


cdef struct AttrValueC:
    attr_id_t attr
    attr_t value

cdef struct TokenPatternC:
    AttrValueC* attrs
    int32_t nr_attr
    quantifier_t quantifier
    hash_t key


cdef struct PatternStateC:
    TokenPatternC* pattern
    int32_t start
    int32_t length


cdef struct MatchC:
    attr_t pattern_id
    int32_t start
    int32_t length


cdef find_matches(TokenPatternC** patterns, int n, Doc doc):
    cdef vector[PatternStateC] states
    cdef vector[MatchC] matches
    cdef PatternStateC state
    cdef Pool mem = Pool()
    # TODO: Prefill this with the extra attribute values.
    extra_attrs = <attr_t**>mem.alloc(len(doc), sizeof(attr_t*))
    # Main loop
    cdef int i, j
    for i in range(doc.length):
        for j in range(n):
            states.push_back(PatternStateC(patterns[j], i, 0))
        transition_states(states, matches, &doc.c[i], extra_attrs[i])
    # Handle matches that end in 0-width patterns
    finish_states(matches, states)
    return [(matches[i].pattern_id, matches[i].start, matches[i].start+matches[i].length)
            for i in range(matches.size())]


cdef attr_t get_ent_id(const TokenPatternC* pattern) nogil:
    # The code was originally designed to always have pattern[1].attrs.value
    # be the ent_id when we get to the end of a pattern. However, Issue #2671
    # showed this wasn't the case when we had a reject-and-continue before a
    # match. I still don't really understand what's going on here, but this
    # workaround does resolve the issue.
    while pattern.attrs.attr != ID and pattern.nr_attr > 0:
        pattern += 1
    return pattern.attrs.value


cdef void transition_states(vector[PatternStateC]& states, vector[MatchC]& matches,
        const TokenC* token, const attr_t* extra_attrs) except *:
    cdef int q = 0
    cdef vector[PatternStateC] new_states
    for i in range(states.size()):
        action = get_action(states[i], token, extra_attrs)
        if action == REJECT:
            continue
        state = states[i]
        states[q] = state
        while action in (RETRY, RETRY_EXTEND):
            if action == RETRY_EXTEND:
                new_states.push_back(
                    PatternStateC(pattern=state.pattern, start=state.start,
                                  length=state.length+1))
            states[q].pattern += 1
            action = get_action(states[q], token, extra_attrs)
        if action == REJECT:
            pass
        elif action == ADVANCE:
            states[q].pattern += 1
            states[q].length += 1
            q += 1
        else:
            ent_id = get_ent_id(&state.pattern[1])
            if action == MATCH:
                matches.push_back(
                    MatchC(pattern_id=ent_id, start=state.start,
                            length=state.length+1))
            elif action == MATCH_REJECT:
                matches.push_back(
                    MatchC(pattern_id=ent_id, start=state.start,
                            length=state.length))
            elif action == MATCH_EXTEND:
                matches.push_back(
                    MatchC(pattern_id=ent_id, start=state.start,
                           length=state.length))
                states[q].length += 1
                q += 1
    states.resize(q)
    for i in range(new_states.size()):
        states.push_back(new_states[i])


cdef void finish_states(vector[MatchC]& matches, vector[PatternStateC]& states) except *:
    '''Handle states that end in zero-width patterns.'''
    cdef PatternStateC state
    for i in range(states.size()):
        state = states[i]
        while get_quantifier(state) in (ZERO_PLUS, ZERO_ONE):
            is_final = get_is_final(state)
            if is_final:
                ent_id = get_ent_id(state.pattern)
                matches.push_back(
                    MatchC(pattern_id=ent_id, start=state.start, length=state.length))
                break
            else:
                state.pattern += 1


cdef action_t get_action(PatternStateC state, const TokenC* token, const attr_t* extra_attrs) nogil:
    '''We need to consider:

    a) Does the token match the specification? [Yes, No]
    b) What's the quantifier? [1, 0+, ?]
    c) Is this the last specification? [final, non-final]

    We can transition in the following ways:

    a) Do we emit a match?
    b) Do we add a state with (next state, next token)?
    c) Do we add a state with (next state, same token)?
    d) Do we add a state with (same state, next token)?

    We'll code the actions as boolean strings, so 0000 means no to all 4,
    1000 means match but no states added, etc.

    1:
      Yes, final:
        1000
      Yes, non-final:
        0100
      No, final:
        0000
      No, non-final
        0000
    0+:
      Yes, final:
        1001
      Yes, non-final:
        0011
      No, final:
        1000 (note: Don't include last token!)
      No, non-final:
        0010
    ?:
      Yes, final:
        1000
      Yes, non-final:
        0100
      No, final:
        1000 (note: Don't include last token!)
      No, non-final:
        0010

    Possible combinations:  1000, 0100, 0000, 1001, 0011, 0010,

    We'll name the bits "match", "advance", "retry", "extend"
    REJECT = 0000
    MATCH = 1000
    ADVANCE = 0100
    RETRY = 0010
    MATCH_EXTEND = 1001
    RETRY_EXTEND = 0011
    MATCH_REJECT = 2000 # Match, but don't include last token

    Problem: If a quantifier is matching, we're adding a lot of open partials
    '''
    cdef char is_match
    is_match = get_is_match(state, token, extra_attrs)
    quantifier = get_quantifier(state)
    is_final = get_is_final(state)
    if quantifier == ZERO:
        is_match = not is_match
        quantifier = ONE
    if quantifier == ONE:
      if is_match and is_final:
          # Yes, final: 1000
          return MATCH
      elif is_match and not is_final:
          # Yes, non-final: 0100
          return ADVANCE
      elif not is_match and is_final:
          # No, final: 0000
          return REJECT
      else:
          return REJECT
    elif quantifier == ZERO_PLUS:
      if is_match and is_final:
          # Yes, final: 1001
          return MATCH_EXTEND
      elif is_match and not is_final:
          # Yes, non-final: 0011
          return RETRY_EXTEND
      elif not is_match and is_final:
          # No, final 2000 (note: Don't include last token!)
          return MATCH_REJECT
      else:
          # No, non-final 0010
          return RETRY
    elif quantifier == ZERO_ONE:
      if is_match and is_final:
          # Yes, final: 1000
          return MATCH
      elif is_match and not is_final:
          # Yes, non-final: 0100
          return ADVANCE
      elif not is_match and is_final:
          # No, final 2000 (note: Don't include last token!)
          return MATCH_REJECT
      else:
          # No, non-final 0010
          return RETRY


cdef char get_is_match(PatternStateC state, const TokenC* token, const attr_t* extra_attrs) nogil:
    spec = state.pattern
    for attr in spec.attrs[:spec.nr_attr]:
        if get_token_attr(token, attr.attr) != attr.value:
            return 0
    else:
        return 1


cdef char get_is_final(PatternStateC state) nogil:
    if state.pattern[1].attrs[0].attr == ID and state.pattern[1].nr_attr == 0:
        return 1
    else:
        return 0


cdef char get_quantifier(PatternStateC state) nogil:
    return state.pattern.quantifier


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
        pattern[i].key = hash64(pattern[i].attrs, pattern[i].nr_attr * sizeof(AttrValueC), 0)
    i = len(token_specs)
    pattern[i].attrs = <AttrValueC*>mem.alloc(2, sizeof(AttrValueC))
    pattern[i].attrs[0].attr = ID
    pattern[i].attrs[0].value = entity_id
    pattern[i].nr_attr = 0
    return pattern


cdef attr_t get_pattern_key(const TokenPatternC* pattern) nogil:
    while pattern.nr_attr != 0:
        pattern += 1
    id_attr = pattern[0].attrs[0]
    if id_attr.attr != ID:
        with gil:
            raise ValueError(Errors.E074.format(attr=ID, bad_attr=id_attr.attr))
    return id_attr.value

def _convert_strings(token_specs, string_store):
    # Support 'syntactic sugar' operator '+', as combination of ONE, ZERO_PLUS
    operators = {'*': (ZERO_PLUS,), '+': (ONE, ZERO_PLUS),
                 '?': (ZERO_ONE,), '1': (ONE,), '!': (ZERO,)}
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
                if attr.upper() == 'TEXT':
                    attr = 'ORTH'
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
        matches = find_matches(&self.patterns[0], self.patterns.size(), doc)
        for i, (key, start, end) in enumerate(matches):
            on_match = self._callbacks.get(key, None)
            if on_match is not None:
                on_match(self, doc, i, matches)
        return matches

    def _normalize_key(self, key):
        if isinstance(key, basestring):
            return self.vocab.strings.add(key)
        else:
            return key


def unpickle_matcher(vocab, patterns, callbacks):
    matcher = Matcher(vocab)
    for key, specs in patterns.items():
        callback = callbacks.get(key, None)
        matcher.add(key, callback, *specs)
    return matcher


def _get_longest_matches(matches):
    '''Filter out matches that have a longer equivalent.'''
    longest_matches = {}
    for pattern_id, start, end in matches:
        key = (pattern_id, start)
        length = end-start
        if key not in longest_matches or length > longest_matches[key]:
            longest_matches[key] = length
    return [(pattern_id, start, start+length)
              for (pattern_id, start), length in longest_matches.items()]


def get_bilou(length):
    if length == 0:
        raise ValueError("Length must be >= 1")
    elif length == 1:
        return [U_ENT]
    elif length == 2:
        return [B2_ENT, L2_ENT]
    elif length == 3:
        return [B3_ENT, I3_ENT, L3_ENT]
    else:
        return [B4_ENT, I4_ENT] + [I4_ENT] * (length-3) + [L4_ENT]


cdef class PhraseMatcher:
    cdef Pool mem
    cdef Vocab vocab
    cdef Matcher matcher
    cdef PreshMap phrase_ids
    cdef int max_length
    cdef attr_id_t attr
    cdef public object _callbacks
    cdef public object _patterns

    def __init__(self, Vocab vocab, max_length=0, attr='ORTH'):
        if max_length != 0:
            deprecation_warning(Warnings.W010)
        self.mem = Pool()
        self.max_length = max_length
        self.vocab = vocab
        self.matcher = Matcher(self.vocab)
        if isinstance(attr, long):
            self.attr = attr
        else:
            self.attr = self.vocab.strings[attr]
        self.phrase_ids = PreshMap()
        abstract_patterns = [
            [{U_ENT: True}],
            [{B2_ENT: True}, {L2_ENT: True}],
            [{B3_ENT: True}, {I3_ENT: True}, {L3_ENT: True}],
            [{B4_ENT: True}, {I4_ENT: True}, {I4_ENT: True, "OP": "+"}, {L4_ENT: True}],
        ]
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
        """Add a match-rule to the phrase-matcher. A match-rule consists of: an ID
        key, an on_match callback, and one or more patterns.

        key (unicode): The match ID.
        on_match (callable): Callback executed on match.
        *docs (Doc): `Doc` objects representing match patterns.
        """
        cdef Doc doc
        cdef hash_t ent_id = self.matcher._normalize_key(key)
        self._callbacks[ent_id] = on_match
        cdef int length
        cdef int i
        cdef hash_t phrase_hash
        cdef Pool mem = Pool()
        for doc in docs:
            length = doc.length
            if length == 0:
                continue
            tags = get_bilou(length)
            phrase_key = <attr_t*>mem.alloc(length, sizeof(attr_t))
            for i, tag in enumerate(tags):
                attr_value = self.get_lex_value(doc, i)
                lexeme = self.vocab[attr_value]
                lexeme.set_flag(tag, True)
                phrase_key[i] = lexeme.orth
            phrase_hash = hash64(phrase_key,
                                 length * sizeof(attr_t), 0)
            self.phrase_ids.set(phrase_hash, <void*>ent_id)

    def __call__(self, Doc doc):

        """Find all sequences matching the supplied patterns on the `Doc`.

        doc (Doc): The document to match over.
        RETURNS (list): A list of `(key, start, end)` tuples,
            describing the matches. A match tuple describes a span
            `doc[start:end]`. The `label_id` and `key` are both integers.
        """
        matches = []
        if self.attr == ORTH:
            match_doc = doc
        else:
            # If we're not matching on the ORTH, match_doc will be a Doc whose
            # token.orth values are the attribute values we're matching on,
            # e.g. Doc(nlp.vocab, words=[token.pos_ for token in doc])
            words = [self.get_lex_value(doc, i) for i in range(len(doc))]
            match_doc = Doc(self.vocab, words=words)
        for _, start, end in self.matcher(match_doc):
            ent_id = self.accept_match(match_doc, start, end)
            if ent_id is not None:
                matches.append((ent_id, start, end))
        for i, (ent_id, start, end) in enumerate(matches):
            on_match = self._callbacks.get(ent_id)
            if on_match is not None:
                on_match(self, doc, i, matches)
        return matches

    def pipe(self, stream, batch_size=1000, n_threads=1, return_matches=False,
             as_tuples=False):
        """Match a stream of documents, yielding them in turn.

        docs (iterable): A stream of documents.
        batch_size (int): Number of documents to accumulate into a working set.
        n_threads (int): The number of threads with which to work on the buffer
            in parallel, if the implementation supports multi-threading.
        return_matches (bool): Yield the match lists along with the docs, making
            results (doc, matches) tuples.
        as_tuples (bool): Interpret the input stream as (doc, context) tuples,
            and yield (result, context) tuples out.
            If both return_matches and as_tuples are True, the output will
            be a sequence of ((doc, matches), context) tuples.
        YIELDS (Doc): Documents, in order.
        """
        if as_tuples:
            for doc, context in stream:
                matches = self(doc)
                if return_matches:
                    yield ((doc, matches), context)
                else:
                    yield (doc, context)
        else:
            for doc in stream:
                matches = self(doc)
                if return_matches:
                    yield (doc, matches)
                else:
                    yield doc

    def accept_match(self, Doc doc, int start, int end):
        cdef int i, j
        cdef Pool mem = Pool()
        phrase_key = <attr_t*>mem.alloc(end-start, sizeof(attr_t))
        for i, j in enumerate(range(start, end)):
            phrase_key[i] = doc.c[j].lex.orth
        cdef hash_t key = hash64(phrase_key,
                                 (end-start) * sizeof(attr_t), 0)
        ent_id = <hash_t>self.phrase_ids.get(key)
        if ent_id == 0:
            return None
        else:
            return ent_id

    def get_lex_value(self, Doc doc, int i):
        if self.attr == ORTH:
            # Return the regular orth value of the lexeme
            return doc.c[i].lex.orth
        # Get the attribute value instead, e.g. token.pos
        attr_value = get_token_attr(&doc.c[i], self.attr)
        if attr_value in (0, 1):
            # Value is boolean, convert to string
            string_attr_value = str(attr_value)
        else:
            string_attr_value = self.vocab.strings[attr_value]
        string_attr_name = self.vocab.strings[self.attr]
        # Concatenate the attr name and value to not pollute lexeme space
        # e.g. 'POS-VERB' instead of just 'VERB', which could otherwise
        # create false positive matches
        return 'matcher:{}-{}'.format(string_attr_name, string_attr_value)


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

    def validateInput(self, pattern, key):
        idx = 0
        visitedNodes = {}
        for relation in pattern:
            if 'PATTERN' not in relation or 'SPEC' not in relation:
                raise ValueError(Errors.E098.format(key=key))
            if idx == 0:
                if not('NODE_NAME' in relation['SPEC'] and 'NBOR_RELOP' not in relation['SPEC'] and 'NBOR_NAME' not in relation['SPEC']):
                    raise ValueError(Errors.E099.format(key=key))
                visitedNodes[relation['SPEC']['NODE_NAME']] = True
            else:
                if not('NODE_NAME' in relation['SPEC'] and 'NBOR_RELOP' in relation['SPEC'] and 'NBOR_NAME' in relation['SPEC']):
                    raise ValueError(Errors.E100.format(key=key))
                if relation['SPEC']['NODE_NAME'] in visitedNodes or relation['SPEC']['NBOR_NAME'] not in visitedNodes:
                    raise ValueError(Errors.E101.format(key=key))
                visitedNodes[relation['SPEC']['NODE_NAME']] = True
                visitedNodes[relation['SPEC']['NBOR_NAME']] = True
            idx = idx + 1

    def add(self, key, on_match, *patterns):
        for pattern in patterns:
            if len(pattern) == 0:
                raise ValueError(Errors.E012.format(key=key))
            self.validateInput(pattern,key)

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
        # Doc-Token based tree cannot be reused since it is memory heavy and
        # tightly coupled with doc
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
                    heads[j] = ('root',j)
                    root = j
                else:
                    heads[j] = (token_pattern['SPEC']['NBOR_RELOP'],_nodes_list[i][token_pattern['SPEC']['NBOR_NAME']])

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
                tree[head].append( (_heads_list[i][j][INDEX_RELOP],j) )
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
                for i in range(len(_nodes)):
                    id_to_position[i]=[]

                # This could be taken outside to improve running time..?
                for match_id, start, end in matches:
                    if match_id in _keys_to_token:
                        id_to_position[_keys_to_token[match_id]].append(start)

                _node_operator_map = self.get_node_operator_map(doc,_tree,id_to_position,_nodes,_root)
                length = len(_nodes)
                if _root in id_to_position:
                    candidates = id_to_position[_root]
                    for candidate in candidates:
                        isVisited = {}
                        self.dfs(candidate,_root,_tree,id_to_position,doc,isVisited,_node_operator_map)
                        # To check if the subtree pattern is completely identified. This is a heuristic.
                        # This is done to reduce the complexity of exponential unordered subtree matching.
                        # Will give approximate matches in some cases.
                        if(len(isVisited) == length):
                            matched_trees.append((key,list(isVisited)))

            for i, (ent_id, nodes) in enumerate(matched_trees):
                on_match = self._callbacks.get(ent_id)
                if on_match is not None:
                    on_match(self, doc, i, matches)

        return matched_trees

    def dfs(self,candidate,root,tree,id_to_position,doc,isVisited,_node_operator_map):
        if(root in id_to_position and candidate in id_to_position[root]):
            # color the node since it is valid
            isVisited[candidate] = True
            if root in tree:
                for root_child in tree[root]:
                    if candidate in _node_operator_map and root_child[INDEX_RELOP] in _node_operator_map[candidate]:
                        candidate_children = _node_operator_map[candidate][root_child[INDEX_RELOP]]
                        for candidate_child in candidate_children:
                            result = self.dfs(
                                candidate_child.i,
                                root_child[INDEX_HEAD],
                                tree,
                                id_to_position,
                                doc,
                                isVisited,
                                _node_operator_map
                            )

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
            '<':self.dep,
            '>':self.gov,
            '>>':self.dep_chain,
            '<<':self.gov_chain,
            '.':self.imm_precede,
            '$+':self.imm_right_sib,
            '$-':self.imm_left_sib,
            '$++':self.right_sib,
            '$--':self.left_sib
        }
        for operator in all_operators:
            for node in all_nodes:
                _node_operator_map[node][operator] = switcher.get(operator)(doc,node)

        return _node_operator_map

    def dep(self,doc,node):
        return list(doc[node].head)

    def gov(self,doc,node):
        return list(doc[node].children)

    def dep_chain(self,doc,node):
        return list(doc[node].ancestors)

    def gov_chain(self,doc,node):
        return list(doc[node].subtree)

    def imm_precede(self,doc,node):
        if node>0:
            return [doc[node-1]]
        return []

    def imm_right_sib(self,doc,node):
        for idx in range(list(doc[node].head.children)):
            if idx == node-1:
                return [doc[idx]]
        return []

    def imm_left_sib(self,doc,node):
        for idx in range(list(doc[node].head.children)):
            if idx == node+1:
                return [doc[idx]]
        return []

    def right_sib(self,doc,node):
        candidate_children = []
        for idx in range(list(doc[node].head.children)):
            if idx < node:
                candidate_children.append(doc[idx])
        return candidate_children

    def left_sib(self,doc,node):
        candidate_children = []
        for idx in range(list(doc[node].head.children)):
            if idx > node:
                candidate_children.append(doc[idx])
        return candidate_children

    def _normalize_key(self, key):
        if isinstance(key, basestring):
            return self.vocab.strings.add(key)
        else:
            return key

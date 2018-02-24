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
from .attrs cimport ID, attr_id_t, NULL_ATTR
from .attrs import IDS
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


cdef struct ActionC:
    char emit_match
    char next_state_next_token
    char next_state_same_token
    char same_state_next_token


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
            ent_id = state.pattern[1].attrs.value
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
                ent_id = state.pattern[1].attrs.value
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
                    msg = "Unknown operator '%s'. Options: %s"
                    raise KeyError(msg % (value, ', '.join(operators.keys())))
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
        *patterns (list): List of token descritions.
        """
        for pattern in patterns:
            if len(pattern) == 0:
                msg = ("Cannot add pattern for zero tokens to matcher.\n"
                       "key: {key}\n")
                raise ValueError(msg.format(key=key))
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
    cdef public object _callbacks
    cdef public object _patterns

    def __init__(self, Vocab vocab, max_length=10):
        self.mem = Pool()
        self.max_length = max_length
        self.vocab = vocab
        self.matcher = Matcher(self.vocab)
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
        """Add a match-rule to the matcher. A match-rule consists of: an ID
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
                lexeme = self.vocab[doc.c[i].lex.orth]
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
        for _, start, end in self.matcher(doc):
            ent_id = self.accept_match(doc, start, end)
            if ent_id is not None:
                matches.append((ent_id, start, end))
        for i, (ent_id, start, end) in enumerate(matches):
            on_match = self._callbacks.get(ent_id)
            if on_match is not None:
                on_match(self, doc, i, matches)
        return matches

    def pipe(self, stream, batch_size=1000, n_threads=2, return_matches=False,
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

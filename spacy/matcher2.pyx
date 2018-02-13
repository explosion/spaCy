# cython: infer_types=True
from libcpp.vector cimport vector
from libc.stdint cimport int32_t, uint64_t
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
    print("N patterns: ", n)
    cdef vector[PatternStateC] init_states
    cdef ActionC null_action = ActionC(-1, -1, -1, -1)
    for i in range(n):
        init_states.push_back(PatternStateC(patterns[i], -1, 0))
    cdef vector[PatternStateC] curr_states
    cdef vector[PatternStateC] nexts
    cdef vector[MatchC] matches
    cdef PreshMap cache
    cdef Pool mem = Pool()
    # TODO: Prefill this with the extra attribute values.
    extra_attrs = <attr_t**>mem.alloc(len(doc), sizeof(attr_t*))
    for i in range(doc.length):
        nexts.clear()
        cache = PreshMap()
        for j in range(curr_states.size()):
            transition(matches, nexts,
                curr_states[j], i, &doc.c[i], extra_attrs[i], cache)
        for j in range(init_states.size()):
            transition(matches, nexts,
                init_states[j], i, &doc.c[i], extra_attrs[i], cache)
        nexts, curr_states = curr_states, nexts
    # Handle patterns that end with zero-width
    for j in range(curr_states.size()):
        state = curr_states[j]
        while get_quantifier(state) in (ZERO_PLUS, ZERO_ONE):
            is_final = get_is_final(state)
            if is_final:
                ent_id = state.pattern[1].attrs.value
                matches.push_back(
                    MatchC(pattern_id=ent_id, start=state.start, length=state.length))
                break
            else:
                state.pattern += 1
    # Filter out matches that have a longer equivalent.
    longest_matches = {}
    for i in range(matches.size()):
        key = (matches[i].pattern_id, matches[i].start)
        length = matches[i].length
        if key not in longest_matches or length > longest_matches[key]:
            longest_matches[key] = length
    return [(pattern_id, start, start+length)
              for (pattern_id, start), length in longest_matches.items()]


cdef void transition(vector[MatchC]& matches, vector[PatternStateC]& nexts,
        PatternStateC state, int i, const TokenC* token, const attr_t* extra_attrs,
        PreshMap cache) except *:
    action = get_action(state, token, extra_attrs, cache)
    if state.start == -1:
        state.start = i
    if action.emit_match == 1:
        ent_id = state.pattern[1].attrs.value
        matches.push_back(
            MatchC(pattern_id=ent_id, start=state.start, length=state.length+1))
    elif action.emit_match == 2:
        ent_id = state.pattern[1].attrs.value
        matches.push_back(
            MatchC(pattern_id=ent_id, start=state.start, length=state.length))
    if action.next_state_next_token:
        nexts.push_back(PatternStateC(start=state.start,
            pattern=&state.pattern[1], length=state.length+1))
    if action.same_state_next_token:
        nexts.push_back(PatternStateC(start=state.start,
            pattern=state.pattern, length=state.length+1))
    cdef PatternStateC next_state
    if action.next_state_same_token:
        # 0+ and ? non-matches need to not consume a token, so we call transition
        # with the same state
        next_state = PatternStateC(start=state.start, pattern=&state.pattern[1],
                                   length=state.length)
        transition(matches, nexts, next_state, i, token, extra_attrs, cache)


cdef ActionC get_action(PatternStateC state, const TokenC* token, const attr_t* extra_attrs,
        PreshMap cache) except *:
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

    Problem: If a quantifier is matching, we're adding a lot of open partials
    '''
    cached_match = <uint64_t>cache.get(state.pattern.key)
    cdef char is_match
    if cached_match == 0:
        is_match = get_is_match(state, token, extra_attrs)
        cached_match = is_match + 1
        cache.set(state.pattern.key, <void*>cached_match)
    elif cached_match == 1:
        is_match = 0
    else:
        is_match = 1
    quantifier = get_quantifier(state)
    is_final = get_is_final(state)
    if quantifier == ZERO:
        is_match = not is_match
        quantifier = ONE
    if quantifier == ONE:
      if is_match and is_final:
          # Yes, final: 1000
          return ActionC(1, 0, 0, 0)
      elif is_match and not is_final:
          # Yes, non-final: 0100
          return ActionC(0, 1, 0, 0)
      elif not is_match and is_final:
          # No, final: 0000
          return ActionC(0, 0, 0, 0)
      else:
          # No, non-final 0000
          return ActionC(0, 0, 0, 0)

    elif quantifier == ZERO_PLUS:
      if is_match and is_final:
          # Yes, final: 1001
          return ActionC(1, 0, 0, 1)
      elif is_match and not is_final:
          # Yes, non-final: 0011
          return ActionC(0, 0, 1, 1)
      elif not is_match and is_final:
          # No, final 1000 (note: Don't include last token!)
          return ActionC(2, 0, 0, 0)
      else:
          # No, non-final 0010
          return ActionC(0, 0, 1, 0)
    elif quantifier == ZERO_ONE:
      if is_match and is_final:
          # Yes, final: 1000
          return ActionC(1, 0, 0, 0)
      elif is_match and not is_final:
          # Yes, non-final: 0100
          return ActionC(0, 1, 0, 0)
      elif not is_match and is_final:
          # No, final 1000 (note: Don't include last token!)
          return ActionC(2, 0, 0, 0)
      else:
          # No, non-final 0010
          return ActionC(0, 0, 1, 0)
    else:
        print(quantifier, is_match, is_final)
        raise ValueError


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
        raise ValueError("Max length currently 10 for phrase matching")


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
                msg = (
                    "Pattern length (%d) >= phrase_matcher.max_length (%d). "
                    "Length can be set on initialization, up to 10."
                )
                raise ValueError(msg % (len(doc), self.max_length))
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
        assert (end - start) < self.max_length
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

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
    char is_match
    char keep_state
    char advance_state


cdef struct PatternStateC:
    TokenPatternC* state
    int32_t pattern_id
    int32_t start
    ActionC last_action


cdef struct MatchC:
    int32_t pattern_id
    int32_t start
    int32_t end


cdef find_matches(TokenPatternC** patterns, int n, Doc doc):
    cdef vector[PatternStateC] init_states
    cdef ActionC null_action = ActionC(-1, -1, -1)
    for i in range(n):
        init_states.push_back(PatternStateC(patterns[i], i, -1, last_action=null_action))
    cdef vector[PatternStateC] curr_states
    cdef vector[PatternStateC] nexts
    cdef vector[MatchC] matches
    cdef PreshMap cache = PreshMap()
    cdef Pool mem = Pool()
    # TODO: Prefill this with the extra attribute values.
    extra_attrs = <attr_t**>mem.alloc(len(doc), sizeof(attr_t*))
    for i in range(doc.length):
        nexts.clear()
        for j in range(curr_states.size()):
            action = get_action(curr_states[j], &doc.c[i], extra_attrs[i], cache)
            transition(matches, nexts,
                action, curr_states[j], i)
        for j in range(init_states.size()):
            action = get_action(init_states[j], &doc.c[i], extra_attrs[i], cache)
            transition(matches, nexts,
                action, init_states[j], i)
        nexts, curr_states = curr_states, nexts
    # Filter out matches that have a longer equivalent.
    longest_matches = {}
    for i in range(matches.size()):
        key = matches[i].pattern_id, matches[i].start
        length = matches[i].end - matches[i].start
        if key not in longest_matches or length > longest_matches[key]:
            longest_matches[key] = length
    return [(pattern_id, start, length-start)
              for (pattern_id, start), length in longest_matches]


cdef void transition(vector[MatchC]& matches, vector[PatternStateC]& nexts,
        ActionC action, PatternStateC state, int token) except *:
    if state.start == -1:
        state.start = token
    if action.is_match:
        matches.push_back(
            MatchC(pattern_id=state.pattern_id, start=state.start, end=token+1))
    if action.keep_state:
        nexts.push_back(PatternStateC(pattern_id=pattern_id,
            start=state.start, state=state.state, last_action=action))
    if action.advance_state:
        nexts.push_back(PatternStateC(pattern_id=pattern_id,
            start=state.start, state=state.state+1, last_action=action))


cdef ActionC get_action(PatternStateC state, const TokenC* token, const attr_t* extra_attrs,
        PreshMap cache) except *:
    '''We need to consider:

    a) Does the token match the specification? [Yes, No]
    b) What's the quantifier? [1, 0+, ?]
    c) Is this the last specification? [final, non-final]

    We therefore have 12 cases to consider. For each case, we need to know
    whether to emit a match, whether to keep the current state in the partials,
    and whether to add an advanced state to the partials.

    We therefore have eight possible results for these three booleans, which
    we'll code as 000, 001 etc.
    
    1:
      - Match, final:
        100
      - Match, non-final:
        001
      - No match:
        000
    0+:
      - Match, final:
        100
      - Match, non-final:
        011
      - Non-match, final:
        100
      - Non-match, non-final:
        010

    Problem: If a quantifier is matching, we're adding a lot of open partials
    Question: Is it worth doing a lookahead, to see if we add?
    '''
    cached_match = <uint64_t>cache.get(state.state.key)
    cdef char is_match
    if cached_match == 0:
        is_match = get_is_match(state, token, extra_attrs)
        cached_match = is_match + 1
        cache.set(state.state.key, <void*>cached_match)
    elif cached_match == 1:
        is_match = 0
    else:
        is_match = 1
    quantifier = get_quantifier(state, token)
    is_final = get_is_final(state, token)
    if quantifier == ONE:
        if not is_match:
            return ActionC(is_match=0, keep_state=0, advance_state=0)
        elif is_final:
            return ActionC(is_match=1, keep_state=0, advance_state=0)
        else:
            return ActionC(is_match=0, keep_state=0, advance_state=1)
    elif quantifier == ZERO_PLUS:
        if is_final:
            return ActionC(is_match=1, keep_state=0, advance_state=0)
        elif is_match:
            return ActionC(is_match=0, keep_state=1, advance_state=1)
        else:
            return ActionC(is_match=0, keep_state=1, advance_state=0)
    elif quantifier == ZERO_ONE:
        if is_final:
            return ActionC(is_match=1, keep_state=0, advance_state=0)
        elif is_match:
            if state.last_action.keep_state:
                return ActionC(is_match=0, keep_state=0, advance_state=1)
            else:
                return ActionC(is_match=0, keep_state=1, advance_state=1)
    else:
        print(quantifier, is_match, is_final)
        raise ValueError


cdef char get_is_match(PatternStateC state, const TokenC* token, const attr_t* extra_attrs) nogil:
    spec = state.state
    for attr in spec.attrs[:spec.nr_attr]:
        if get_token_attr(token, attr.attr) != attr.value:
            return 0
    else:
        return 1


cdef char get_is_final(PatternStateC state, const TokenC* token) nogil:
    if state.state[1].attrs[0].attr == ID and state.state[1].nr_attr == 0:
        return 1
    else:
        return 0


cdef char get_quantifier(PatternStateC state, const TokenC* token) nogil:
    return state.state.quantifier


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

    def __call__(self, Doc doc):
        """Find all token sequences matching the supplied pattern.

        doc (Doc): The document to match over.
        RETURNS (list): A list of `(key, start, end)` tuples,
            describing the matches. A match tuple describes a span
            `doc[start:end]`. The `label_id` and `key` are both integers.
        """
        matches = find_matches(&self.patterns[0], self.patterns.size(), doc)
        return matches


def unpickle_matcher(vocab, patterns, callbacks):
    matcher = Matcher(vocab)
    for key, specs in patterns.items():
        callback = callbacks.get(key, None)
        matcher.add(key, callback, *specs)
    return matcher


 

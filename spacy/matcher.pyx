# cython: profile=True
# cython: infer_types=True
from __future__ import unicode_literals

from os import path

from .typedefs cimport attr_t
from .typedefs cimport hash_t
from .attrs cimport attr_id_t
from .structs cimport TokenC, LexemeC
from .lexeme cimport Lexeme

from cymem.cymem cimport Pool
from preshed.maps cimport PreshMap
from libcpp.vector cimport vector
from libcpp.pair cimport pair
from murmurhash.mrmr cimport hash64
from libc.stdint cimport int32_t

from .attrs cimport ID, LENGTH, ENT_TYPE, ORTH, NORM, LEMMA, LOWER, SHAPE
from . import attrs
from .tokens.doc cimport get_token_attr
from .tokens.doc cimport Doc
from .vocab cimport Vocab

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


try:
    import ujson as json
except ImportError:
    import json


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
    PANIC


cdef struct AttrValueC:
    attr_id_t attr
    attr_t value


cdef struct TokenPatternC:
    AttrValueC* attrs
    int32_t nr_attr
    quantifier_t quantifier


ctypedef TokenPatternC* TokenPatternC_ptr
ctypedef pair[int, TokenPatternC_ptr] StateC


cdef TokenPatternC* init_pattern(Pool mem, attr_t entity_id, attr_t label,
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
    pattern[i].attrs = <AttrValueC*>mem.alloc(3, sizeof(AttrValueC))
    pattern[i].attrs[0].attr = ID
    pattern[i].attrs[0].value = entity_id
    pattern[i].attrs[1].attr = ENT_TYPE
    pattern[i].attrs[1].value = label
    pattern[i].nr_attr = 0
    return pattern


cdef int get_action(const TokenPatternC* pattern, const TokenC* token) nogil:
    for attr in pattern.attrs[:pattern.nr_attr]:
        if get_token_attr(token, attr.attr) != attr.value:
            if pattern.quantifier == ONE:
                return REJECT
            elif pattern.quantifier == ZERO:
                return ACCEPT if (pattern+1).nr_attr == 0 else ADVANCE
            elif pattern.quantifier in (ZERO_ONE, ZERO_PLUS):
                return ACCEPT if (pattern+1).nr_attr == 0 else ADVANCE_ZERO
            else:
                return PANIC
    if pattern.quantifier == ZERO:
        return REJECT
    elif pattern.quantifier in (ONE, ZERO_ONE):
        return ACCEPT if (pattern+1).nr_attr == 0 else ADVANCE
    elif pattern.quantifier == ZERO_PLUS:
        return REPEAT
    else:
        return PANIC


def _convert_strings(token_specs, string_store):
    # Support 'syntactic sugar' operator '+', as combination of ONE, ZERO_PLUS
    operators = {'!': (ZERO,), '*': (ZERO_PLUS,), '+': (ONE, ZERO_PLUS),
                 '?': (ZERO_ONE,)}
    tokens = []
    op = ONE
    for spec in token_specs:
        token = []
        ops = (ONE,)
        for attr, value in spec.items():
            if isinstance(attr, basestring) and attr.upper() == 'OP':
                if value in operators:
                    ops = operators[value]
                else:
                    raise KeyError(
                        "Unknown operator. Options: %s" % ', '.join(operators.keys()))
            if isinstance(attr, basestring):
                attr = attrs.IDS.get(attr.upper())
            if isinstance(value, basestring):
                value = string_store[value]
            if isinstance(value, bool):
                value = int(value)
            if attr is not None:
                token.append((attr, value))
        for op in ops:
            tokens.append((op, token))
    return tokens


cdef class Matcher:
    '''Match sequences of tokens, based on pattern rules.'''
    cdef Pool mem
    cdef vector[TokenPatternC*] patterns
    cdef readonly Vocab vocab
    cdef public object _patterns
    cdef public object _entities
    cdef public object _callbacks
    cdef public object _acceptors

    @classmethod
    def load(cls, path, vocab):
        '''Load the matcher and patterns from a file path.

        Arguments:
            path (Path):
                Path to a JSON-formatted patterns file.
            vocab (Vocab):
                The vocabulary that the documents to match over will refer to.
        Returns:
            Matcher: The newly constructed object.
        '''
        if (path / 'gazetteer.json').exists():
            with (path / 'gazetteer.json').open('r', encoding='utf8') as file_:
                patterns = json.load(file_)
        else:
            patterns = {}
        return cls(vocab, patterns)

    def __init__(self, vocab, patterns={}):
        """Create the Matcher.

        Arguments:
            vocab (Vocab):
                The vocabulary object, which must be shared with the documents
                the matcher will operate on.
            patterns (dict): Patterns to add to the matcher.
        Returns:
            The newly constructed object.
        """
        self._patterns = {}
        self._entities = {}
        self._acceptors = {}
        self._callbacks = {}
        self.vocab = vocab
        self.mem = Pool()
        for entity_key, (etype, attrs, specs) in sorted(patterns.items()):
            self.add_entity(entity_key, attrs)
            for spec in specs:
                self.add_pattern(entity_key, spec, label=etype)

    def __reduce__(self):
        return (self.__class__, (self.vocab, self._patterns), None, None)

    property n_patterns:
        def __get__(self): return self.patterns.size()

    def add_entity(self, entity_key, attrs=None, if_exists='raise',
                   acceptor=None, on_match=None):
        """Add an entity to the matcher.

        Arguments:
            entity_key (unicode or int):
                An ID for the entity.
            attrs:
                Attributes to associate with the Matcher.
            if_exists ('raise', 'ignore' or 'update'):
                Controls what happens if the entity ID already exists. Defaults to 'raise'.
            acceptor:
                Callback function to filter matches of the entity.
            on_match:
                Callback function to act on matches of the entity.
        Returns:
            None
        """
        if if_exists not in ('raise', 'ignore', 'update'):
            raise ValueError(
                "Unexpected value for if_exists: %s.\n"
                "Expected one of: ['raise', 'ignore', 'update']" % if_exists)
        if attrs is None:
            attrs = {}
        entity_key = self.normalize_entity_key(entity_key)
        if self.has_entity(entity_key):
            if if_exists == 'raise':
                raise KeyError(
                    "Tried to add entity %s. Entity exists, and if_exists='raise'.\n"
                    "Set if_exists='ignore' or if_exists='update', or check with "
                    "matcher.has_entity()")
            elif if_exists == 'ignore':
                return
        self._entities[entity_key] = dict(attrs)
        self._patterns.setdefault(entity_key, [])
        self._acceptors[entity_key] = acceptor
        self._callbacks[entity_key] = on_match

    def add_pattern(self, entity_key, token_specs, label=""):
        """Add a pattern to the matcher.

        Arguments:
            entity_key (unicode or int):
                An ID for the entity.
            token_specs:
                Description of the pattern to be matched.
            label:
                Label to assign to the matched pattern. Defaults to "".
        Returns:
            None
        """
        token_specs = list(token_specs)
        if len(token_specs) == 0:
            msg = ("Cannot add pattern for zero tokens to matcher.\n"
                   "entity_key: {entity_key}\n"
                   "label: {label}")
            raise ValueError(msg.format(entity_key=entity_key, label=label))
        entity_key = self.normalize_entity_key(entity_key)
        if not self.has_entity(entity_key):
            self.add_entity(entity_key)
        if isinstance(label, basestring):
            label = self.vocab.strings[label]
        elif label is None:
            label = 0
        spec = _convert_strings(token_specs, self.vocab.strings)

        self.patterns.push_back(init_pattern(self.mem, entity_key, label, spec))
        self._patterns[entity_key].append((label, token_specs))

    def add(self, entity_key, label, attrs, specs, acceptor=None, on_match=None):
        self.add_entity(entity_key, attrs=attrs, if_exists='update',
                        acceptor=acceptor, on_match=on_match)
        for spec in specs:
            self.add_pattern(entity_key, spec, label=label)

    def normalize_entity_key(self, entity_key):
        if isinstance(entity_key, basestring):
            return self.vocab.strings[entity_key]
        else:
            return entity_key

    def has_entity(self, entity_key):
        """Check whether the matcher has an entity.

        Arguments:
            entity_key (string or int): The entity key to check.
        Returns:
            bool: Whether the matcher has the entity.
        """
        entity_key = self.normalize_entity_key(entity_key)
        return entity_key in self._entities

    def get_entity(self, entity_key):
        """Retrieve the attributes stored for an entity.

        Arguments:
            entity_key (unicode or int): The entity to retrieve.
        Returns:
            The entity attributes if present, otherwise None.
        """
        entity_key = self.normalize_entity_key(entity_key)
        if entity_key in self._entities:
            return self._entities[entity_key]
        else:
            return None

    def __call__(self, Doc doc, acceptor=None):
        """Find all token sequences matching the supplied patterns on the Doc.

        Arguments:
            doc (Doc):
                The document to match over.
        Returns:
            list
            A list of (entity_key, label_id, start, end) tuples,
            describing the matches. A match tuple describes a span doc[start:end].
            The label_id and entity_key are both integers.
        """
        if acceptor is not None:
            raise ValueError(
                "acceptor keyword argument to Matcher deprecated. Specify acceptor "
                "functions when you add patterns instead.")
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
            # Go over the open matches, extending or finalizing if able. Otherwise,
            # we over-write them (q doesn't advance)
            for state in partials:
                action = get_action(state.second, token)
                if action == PANIC:
                    raise Exception("Error selecting action in matcher")
                while action == ADVANCE_ZERO:
                    state.second += 1
                    action = get_action(state.second, token)
                if action == REPEAT:
                    # Leave the state in the queue, and advance to next slot
                    # (i.e. we don't overwrite -- we want to greedily match more
                    # pattern.
                    q += 1
                elif action == REJECT:
                    pass
                elif action == ADVANCE:
                    partials[q] = state
                    partials[q].second += 1
                    q += 1
                elif action == ACCEPT:
                    # TODO: What to do about patterns starting with ZERO? Need to
                    # adjust the start position.
                    start = state.first
                    end = token_i+1
                    ent_id = state.second[1].attrs[0].value
                    label = state.second[1].attrs[1].value
                    acceptor = self._acceptors.get(ent_id)
                    if acceptor is None:
                        matches.append((ent_id, label, start, end))
                    else:
                        match = acceptor(doc, ent_id, label, start, end)
                        if match:
                            matches.append(match)
            partials.resize(q)
            # Check whether we open any new patterns on this token
            for pattern in self.patterns:
                action = get_action(pattern, token)
                if action == PANIC:
                    raise Exception("Error selecting action in matcher")
                while action == ADVANCE_ZERO:
                    pattern += 1
                    action = get_action(pattern, token)
                if action == REPEAT:
                    state.first = token_i
                    state.second = pattern
                    partials.push_back(state)
                elif action == ADVANCE:
                    # TODO: What to do about patterns starting with ZERO? Need to
                    # adjust the start position.
                    state.first = token_i
                    state.second = pattern + 1
                    partials.push_back(state)
                elif action == ACCEPT:
                    start = token_i
                    end = token_i+1
                    ent_id = pattern[1].attrs[0].value
                    label = pattern[1].attrs[1].value
                    acceptor = self._acceptors.get(ent_id)
                    if acceptor is None:
                        matches.append((ent_id, label, start, end))
                    else:
                        match = acceptor(doc, ent_id, label, start, end)
                        if match:
                            matches.append(match)
        for i, (ent_id, label, start, end) in enumerate(matches):
            on_match = self._callbacks.get(ent_id)
            if on_match is not None:
                on_match(self, doc, i, matches)
        return matches

    def pipe(self, docs, batch_size=1000, n_threads=2):
        """Match a stream of documents, yielding them in turn.

        Arguments:
            docs: A stream of documents.
            batch_size (int):
                The number of documents to accumulate into a working set.
            n_threads (int):
                The number of threads with which to work on the buffer in parallel,
                if the Matcher implementation supports multi-threading.
        Yields:
            Doc Documents, in order.
        """
        for doc in docs:
            self(doc)
            yield doc


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
        return [B9_ENT, I9_ENT, I9_ENT, I9_ENT, I9_ENT, I9_ENT, I9_ENT, I9_ENT, L9_ENT]
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

    def __init__(self, Vocab vocab, phrases, max_length=10):
        self.mem = Pool()
        self._phrase_key = <attr_t*>self.mem.alloc(max_length, sizeof(attr_t))
        self.max_length = max_length
        self.vocab = vocab
        self.matcher = Matcher(self.vocab, {})
        self.phrase_ids = PreshMap()
        for phrase in phrases:
            if len(phrase) < max_length:
                self.add(phrase)

        abstract_patterns = []
        for length in range(1, max_length):
            abstract_patterns.append([{tag: True} for tag in get_bilou(length)])
        self.matcher.add('Candidate', 'MWE', {}, abstract_patterns, acceptor=self.accept_match)

    def add(self, Doc tokens):
        cdef int length = tokens.length
        assert length < self.max_length
        tags = get_bilou(length)
        assert len(tags) == length, length

        cdef int i
        for i in range(self.max_length):
            self._phrase_key[i] = 0
        for i, tag in enumerate(tags):
            lexeme = self.vocab[tokens.c[i].lex.orth]
            lexeme.set_flag(tag, True)
            self._phrase_key[i] = lexeme.orth
        cdef hash_t key = hash64(self._phrase_key, self.max_length * sizeof(attr_t), 0)
        self.phrase_ids[key] = True

    def __call__(self, Doc doc):
        matches = []
        for ent_id, label, start, end in self.matcher(doc):
            cand = doc[start : end]
            start = cand[0].idx
            end = cand[-1].idx + len(cand[-1])
            matches.append((start, end, cand.root.tag_, cand.text, 'MWE'))
        for match in matches:
            doc.merge(*match)
        return matches

    def pipe(self, stream, batch_size=1000, n_threads=2):
        for doc in stream:
            self(doc)
            yield doc

    def accept_match(self, Doc doc, int ent_id, int label, int start, int end):
        assert (end - start) < self.max_length
        cdef int i, j
        for i in range(self.max_length):
            self._phrase_key[i] = 0
        for i, j in enumerate(range(start, end)):
            self._phrase_key[i] = doc.c[j].lex.orth
        cdef hash_t key = hash64(self._phrase_key, self.max_length * sizeof(attr_t), 0)
        if self.phrase_ids.get(key):
            return (ent_id, label, start, end)
        else:
            return False

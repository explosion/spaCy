# cython: infer_types=True
# cython: profile=True
from __future__ import unicode_literals

from cymem.cymem cimport Pool
from murmurhash.mrmr cimport hash64
from preshed.maps cimport PreshMap

from .matcher cimport Matcher
from ..attrs cimport ORTH, POS, TAG, DEP, LEMMA, attr_id_t
from ..vocab cimport Vocab
from ..tokens.doc cimport Doc, get_token_attr
from ..typedefs cimport attr_t, hash_t

from ..errors import Errors, Warnings, deprecation_warning, user_warning
from ..attrs import FLAG61 as U_ENT
from ..attrs import FLAG60 as B2_ENT
from ..attrs import FLAG59 as B3_ENT
from ..attrs import FLAG58 as B4_ENT
from ..attrs import FLAG43 as L2_ENT
from ..attrs import FLAG42 as L3_ENT
from ..attrs import FLAG41 as L4_ENT
from ..attrs import FLAG42 as I3_ENT
from ..attrs import FLAG41 as I4_ENT


cdef class PhraseMatcher:
    """Efficiently match large terminology lists. While the `Matcher` matches
    sequences based on lists of token descriptions, the `PhraseMatcher` accepts
    match patterns in the form of `Doc` objects.

    DOCS: https://spacy.io/api/phrasematcher
    USAGE: https://spacy.io/usage/rule-based-matching#phrasematcher
    """
    cdef Pool mem
    cdef Vocab vocab
    cdef Matcher matcher
    cdef PreshMap phrase_ids
    cdef int max_length
    cdef attr_id_t attr
    cdef public object _callbacks
    cdef public object _patterns
    cdef public object _docs
    cdef public object _validate

    def __init__(self, Vocab vocab, max_length=0, attr="ORTH", validate=False):
        """Initialize the PhraseMatcher.

        vocab (Vocab): The shared vocabulary.
        attr (int / unicode): Token attribute to match on.
        validate (bool): Perform additional validation when patterns are added.
        RETURNS (PhraseMatcher): The newly constructed object.

        DOCS: https://spacy.io/api/phrasematcher#init
        """
        if max_length != 0:
            deprecation_warning(Warnings.W010)
        self.mem = Pool()
        self.max_length = max_length
        self.vocab = vocab
        self.matcher = Matcher(self.vocab, validate=False)
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
        self.matcher.add("Candidate", None, *abstract_patterns)
        self._callbacks = {}
        self._docs = {}
        self._validate = validate

    def __len__(self):
        """Get the number of rules added to the matcher. Note that this only
        returns the number of rules (identical with the number of IDs), not the
        number of individual patterns.

        RETURNS (int): The number of rules.

        DOCS: https://spacy.io/api/phrasematcher#len
        """
        return len(self._docs)

    def __contains__(self, key):
        """Check whether the matcher contains rules for a match ID.

        key (unicode): The match ID.
        RETURNS (bool): Whether the matcher contains rules for this match ID.

        DOCS: https://spacy.io/api/phrasematcher#contains
        """
        cdef hash_t ent_id = self.matcher._normalize_key(key)
        return ent_id in self._callbacks

    def __reduce__(self):
        data = (self.vocab, self._docs, self._callbacks)
        return (unpickle_matcher, data, None, None)

    def add(self, key, on_match, *docs):
        """Add a match-rule to the phrase-matcher. A match-rule consists of: an ID
        key, an on_match callback, and one or more patterns.

        key (unicode): The match ID.
        on_match (callable): Callback executed on match.
        *docs (Doc): `Doc` objects representing match patterns.

        DOCS: https://spacy.io/api/phrasematcher#add
        """
        cdef Doc doc
        cdef hash_t ent_id = self.matcher._normalize_key(key)
        self._callbacks[ent_id] = on_match
        self._docs[ent_id] = docs
        cdef int length
        cdef int i
        cdef hash_t phrase_hash
        cdef Pool mem = Pool()
        for doc in docs:
            length = doc.length
            if length == 0:
                continue
            if self._validate and (doc.is_tagged or doc.is_parsed) \
              and self.attr not in (DEP, POS, TAG, LEMMA):
                string_attr = self.vocab.strings[self.attr]
                user_warning(Warnings.W012.format(key=key, attr=string_attr))
            tags = get_bilou(length)
            phrase_key = <attr_t*>mem.alloc(length, sizeof(attr_t))
            for i, tag in enumerate(tags):
                attr_value = self.get_lex_value(doc, i)
                lexeme = self.vocab[attr_value]
                lexeme.set_flag(tag, True)
                phrase_key[i] = lexeme.orth
            phrase_hash = hash64(phrase_key, length * sizeof(attr_t), 0)
            self.phrase_ids.set(phrase_hash, <void*>ent_id)

    def __call__(self, Doc doc):
        """Find all sequences matching the supplied patterns on the `Doc`.

        doc (Doc): The document to match over.
        RETURNS (list): A list of `(key, start, end)` tuples,
            describing the matches. A match tuple describes a span
            `doc[start:end]`. The `label_id` and `key` are both integers.

        DOCS: https://spacy.io/api/phrasematcher#call
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

    def pipe(self, stream, batch_size=1000, n_threads=-1, return_matches=False,
             as_tuples=False):
        """Match a stream of documents, yielding them in turn.

        docs (iterable): A stream of documents.
        batch_size (int): Number of documents to accumulate into a working set.
        return_matches (bool): Yield the match lists along with the docs, making
            results (doc, matches) tuples.
        as_tuples (bool): Interpret the input stream as (doc, context) tuples,
            and yield (result, context) tuples out.
            If both return_matches and as_tuples are True, the output will
            be a sequence of ((doc, matches), context) tuples.
        YIELDS (Doc): Documents, in order.

        DOCS: https://spacy.io/api/phrasematcher#pipe
        """
        if n_threads != -1:
            deprecation_warning(Warnings.W016)
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
        cdef hash_t key = hash64(phrase_key, (end-start) * sizeof(attr_t), 0)
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
        return "matcher:{}-{}".format(string_attr_name, string_attr_value)


def get_bilou(length):
    if length == 0:
        raise ValueError(Errors.E127)
    elif length == 1:
        return [U_ENT]
    elif length == 2:
        return [B2_ENT, L2_ENT]
    elif length == 3:
        return [B3_ENT, I3_ENT, L3_ENT]
    else:
        return [B4_ENT, I4_ENT] + [I4_ENT] * (length-3) + [L4_ENT]


def unpickle_matcher(vocab, docs, callbacks):
    matcher = PhraseMatcher(vocab)
    for key, specs in docs.items():
        callback = callbacks.get(key, None)
        matcher.add(key, callback, *specs)
    return matcher

# cython: infer_types=True
from preshed.maps cimport map_clear, map_get, map_init, map_iter, map_set

import warnings

from ..attrs cimport DEP, LEMMA, MORPH, POS, TAG

from ..attrs import IDS

from ..tokens.span cimport Span
from ..tokens.token cimport Token
from ..typedefs cimport attr_t

from ..errors import Errors, Warnings
from ..schemas import TokenPattern


cdef class PhraseMatcher:
    """Efficiently match large terminology lists. While the `Matcher` matches
    sequences based on lists of token descriptions, the `PhraseMatcher` accepts
    match patterns in the form of `Doc` objects.

    DOCS: https://spacy.io/api/phrasematcher
    USAGE: https://spacy.io/usage/rule-based-matching#phrasematcher

    Adapted from FlashText: https://github.com/vi3k6i5/flashtext
    MIT License (see `LICENSE`)
    Copyright (c) 2017 Vikash Singh (vikash.duliajan@gmail.com)
    """

    def __init__(self, Vocab vocab, attr="ORTH", validate=False):
        """Initialize the PhraseMatcher.

        vocab (Vocab): The shared vocabulary.
        attr (int / str): Token attribute to match on.
        validate (bool): Perform additional validation when patterns are added.

        DOCS: https://spacy.io/api/phrasematcher#init
        """
        self.vocab = vocab
        self._callbacks = {}
        self._docs = {}
        self._validate = validate

        self.mem = Pool()
        self.c_map = <MapStruct*>self.mem.alloc(1, sizeof(MapStruct))
        self._terminal_hash = 826361138722620965
        map_init(self.mem, self.c_map, 8)

        if isinstance(attr, int):
            self.attr = attr
        else:
            if attr is None:
                attr = "ORTH"
            attr = attr.upper()
            if attr == "TEXT":
                attr = "ORTH"
            if attr == "IS_SENT_START":
                attr = "SENT_START"
            if attr.lower() not in TokenPattern().dict():
                raise ValueError(Errors.E152.format(attr=attr))
            self.attr = IDS.get(attr)

    def __len__(self):
        """Get the number of match IDs added to the matcher.

        RETURNS (int): The number of rules.

        DOCS: https://spacy.io/api/phrasematcher#len
        """
        return len(self._callbacks)

    def __contains__(self, key):
        """Check whether the matcher contains rules for a match ID.

        key (str): The match ID.
        RETURNS (bool): Whether the matcher contains rules for this match ID.

        DOCS: https://spacy.io/api/phrasematcher#contains
        """
        return key in self._callbacks

    def __reduce__(self):
        data = (self.vocab, self._docs, self._callbacks, self.attr)
        return (unpickle_matcher, data, None, None)

    def remove(self, key):
        """Remove a rule from the matcher by match ID. A KeyError is raised if
        the key does not exist.

        key (str): The match ID.

        DOCS: https://spacy.io/api/phrasematcher#remove
        """
        if key not in self._docs:
            raise KeyError(key)
        cdef MapStruct* current_node
        cdef MapStruct* terminal_map
        cdef MapStruct* node_pointer
        cdef void* result
        cdef key_t terminal_key
        cdef void* value
        cdef int c_i = 0
        cdef vector[MapStruct*] path_nodes
        cdef vector[key_t] path_keys
        cdef key_t key_to_remove
        for keyword in sorted(self._docs[key], key=lambda x: len(x), reverse=True):
            current_node = self.c_map
            path_nodes.clear()
            path_keys.clear()
            for token in keyword:
                result = map_get(current_node, token)
                if result:
                    path_nodes.push_back(current_node)
                    path_keys.push_back(token)
                    current_node = <MapStruct*>result
                else:
                    # if token is not found, break out of the loop
                    current_node = NULL
                    break
            path_nodes.push_back(current_node)
            path_keys.push_back(self._terminal_hash)
            # remove the tokens from trie node if there are no other
            # keywords with them
            result = map_get(current_node, self._terminal_hash)
            if current_node != NULL and result:
                terminal_map = <MapStruct*>result
                terminal_keys = []
                c_i = 0
                while map_iter(terminal_map, &c_i, &terminal_key, &value):
                    terminal_keys.append(self.vocab.strings[terminal_key])
                # if this is the only remaining key, remove unnecessary paths
                if terminal_keys == [key]:
                    while not path_nodes.empty():
                        node_pointer = path_nodes.back()
                        path_nodes.pop_back()
                        key_to_remove = path_keys.back()
                        path_keys.pop_back()
                        result = map_get(node_pointer, key_to_remove)
                        if node_pointer.filled == 1:
                            map_clear(node_pointer, key_to_remove)
                            self.mem.free(result)
                        else:
                            # more than one key means more than 1 path,
                            # delete not required path and keep the others
                            map_clear(node_pointer, key_to_remove)
                            self.mem.free(result)
                            break
                # otherwise simply remove the key
                else:
                    result = map_get(current_node, self._terminal_hash)
                    if result:
                        map_clear(<MapStruct*>result, self.vocab.strings[key])

        del self._callbacks[key]
        del self._docs[key]

    def add(self, key, docs, *_docs, on_match=None):
        """Add a match-rule to the phrase-matcher. A match-rule consists of: an ID
        key, an on_match callback, and one or more patterns.

        Since spaCy v2.2.2, PhraseMatcher.add takes a list of patterns as the
        second argument, with the on_match callback as an optional keyword
        argument.

        key (str): The match ID.
        docs (list): List of `Doc` objects representing match patterns.
        on_match (callable): Callback executed on match.
        *_docs (Doc): For backwards compatibility: list of patterns to add
            as variable arguments. Will be ignored if a list of patterns is
            provided as the second argument.

        DOCS: https://spacy.io/api/phrasematcher#add
        """
        if docs is None or hasattr(docs, "__call__"):  # old API
            on_match = docs
            docs = _docs

        _ = self.vocab[key]
        self._callbacks[key] = on_match
        self._docs.setdefault(key, set())

        cdef MapStruct* current_node
        cdef MapStruct* internal_node
        cdef void* result

        if isinstance(docs, Doc):
            raise ValueError(Errors.E179.format(key=key))
        for doc in docs:
            if len(doc) == 0:
                continue
            if isinstance(doc, Doc):
                attrs = (TAG, POS, MORPH, LEMMA, DEP)
                has_annotation = {attr: doc.has_annotation(attr) for attr in attrs}
                for attr in attrs:
                    if self.attr == attr and not has_annotation[attr]:
                        if attr == TAG:
                            pipe = "tagger"
                        elif attr in (POS, MORPH):
                            pipe = "morphologizer or tagger+attribute_ruler"
                        elif attr == LEMMA:
                            pipe = "lemmatizer"
                        elif attr == DEP:
                            pipe = "parser"
                        error_msg = Errors.E155.format(pipe=pipe, attr=self.vocab.strings.as_string(attr))
                        raise ValueError(error_msg)
                if self._validate and any(has_annotation.values()) \
                        and self.attr not in attrs:
                    string_attr = self.vocab.strings[self.attr]
                    warnings.warn(Warnings.W012.format(key=key, attr=string_attr))
                keyword = self._convert_to_array(doc)
            else:
                keyword = doc
            self._docs[key].add(tuple(keyword))

            current_node = self.c_map
            for token in keyword:
                if token == self._terminal_hash:
                    warnings.warn(Warnings.W021)
                    break
                result = <MapStruct*>map_get(current_node, token)
                if not result:
                    internal_node = <MapStruct*>self.mem.alloc(1, sizeof(MapStruct))
                    map_init(self.mem, internal_node, 8)
                    map_set(self.mem, current_node, token, internal_node)
                    result = internal_node
                current_node = <MapStruct*>result
            result = <MapStruct*>map_get(current_node, self._terminal_hash)
            if not result:
                internal_node = <MapStruct*>self.mem.alloc(1, sizeof(MapStruct))
                map_init(self.mem, internal_node, 8)
                map_set(self.mem, current_node, self._terminal_hash, internal_node)
                result = internal_node
            map_set(self.mem, <MapStruct*>result, self.vocab.strings[key], NULL)

    def __call__(self, object doclike, *, as_spans=False):
        """Find all sequences matching the supplied patterns on the `Doc`.

        doclike (Doc or Span): The document to match over.
        as_spans (bool): Return Span objects with labels instead of (match_id,
            start, end) tuples.
        RETURNS (list): A list of `(match_id, start, end)` tuples,
            describing the matches. A match tuple describes a span
            `doc[start:end]`. The `match_id` is an integer. If as_spans is set
            to True, a list of Span objects is returned.

        DOCS: https://spacy.io/api/phrasematcher#call
        """
        matches = []
        if doclike is None or len(doclike) == 0:
            # if doc is empty or None just return empty list
            return matches
        if isinstance(doclike, Doc):
            doc = doclike
            start_idx = 0
            end_idx = len(doc)
        elif isinstance(doclike, Span):
            doc = doclike.doc
            start_idx = doclike.start
            end_idx = doclike.end
        else:
            raise ValueError(Errors.E195.format(good="Doc or Span", got=type(doclike).__name__))

        cdef vector[SpanC] c_matches
        self.find_matches(doc, start_idx, end_idx, &c_matches)
        for i in range(c_matches.size()):
            matches.append((c_matches[i].label, c_matches[i].start, c_matches[i].end))
        for i, (ent_id, start, end) in enumerate(matches):
            on_match = self._callbacks.get(self.vocab.strings[ent_id])
            if on_match is not None:
                on_match(self, doc, i, matches)
        if as_spans:
            return [Span(doc, start, end, label=key) for key, start, end in matches]
        else:
            return matches

    cdef void find_matches(self, Doc doc, int start_idx, int end_idx, vector[SpanC] *matches) nogil:
        cdef MapStruct* current_node = self.c_map
        cdef int start = 0
        cdef int idx = start_idx
        cdef int idy = start_idx
        cdef key_t key
        cdef void* value
        cdef int i = 0
        cdef SpanC ms
        cdef void* result
        while idx < end_idx:
            start = idx
            token = Token.get_struct_attr(&doc.c[idx], self.attr)
            # look for sequences from this position
            result = map_get(current_node, token)
            if result:
                current_node = <MapStruct*>result
                idy = idx + 1
                while idy < end_idx:
                    result = map_get(current_node, self._terminal_hash)
                    if result:
                        i = 0
                        while map_iter(<MapStruct*>result, &i, &key, &value):
                            ms = make_spanstruct(key, start, idy)
                            matches.push_back(ms)
                    inner_token = Token.get_struct_attr(&doc.c[idy], self.attr)
                    result = map_get(current_node, inner_token)
                    if result:
                        current_node = <MapStruct*>result
                        idy += 1
                    else:
                        break
                else:
                    # end of doc reached
                    result = map_get(current_node, self._terminal_hash)
                    if result:
                        i = 0
                        while map_iter(<MapStruct*>result, &i, &key, &value):
                            ms = make_spanstruct(key, start, idy)
                            matches.push_back(ms)
            current_node = self.c_map
            idx += 1

    def pipe(self, stream, batch_size=1000, return_matches=False, as_tuples=False):
        """Match a stream of documents, yielding them in turn. Deprecated as of
        spaCy v3.0.
        """
        warnings.warn(Warnings.W105.format(matcher="PhraseMatcher"), DeprecationWarning)
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

    def _convert_to_array(self, Doc doc):
        return [Token.get_struct_attr(&doc.c[i], self.attr) for i in range(len(doc))]


def unpickle_matcher(vocab, docs, callbacks, attr):
    matcher = PhraseMatcher(vocab, attr=attr)
    for key, specs in docs.items():
        callback = callbacks.get(key, None)
        matcher.add(key, specs, on_match=callback)
    return matcher


cdef SpanC make_spanstruct(attr_t label, int start, int end) nogil:
    cdef SpanC spanc
    spanc.label = label
    spanc.start = start
    spanc.end = end
    return spanc

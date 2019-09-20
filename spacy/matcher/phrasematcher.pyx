# cython: infer_types=True
# cython: profile=True
from __future__ import unicode_literals

import numpy as np

from ..attrs cimport ORTH, POS, TAG, DEP, LEMMA, attr_id_t
from ..vocab cimport Vocab
from ..tokens.doc cimport Doc, get_token_attr

from ._schemas import TOKEN_PATTERN_SCHEMA
from ..errors import Errors, Warnings, deprecation_warning, user_warning


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
    cdef Vocab vocab
    cdef unicode _terminal
    cdef object keyword_trie_dict
    cdef attr_id_t attr
    cdef object _callbacks
    cdef object _keywords
    cdef object _docs
    cdef bint _validate

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
        self.vocab = vocab
        self._terminal = '_terminal_'
        self.keyword_trie_dict = dict()
        self._callbacks = {}
        self._keywords = {}
        self._docs = {}
        self._validate = validate

        if isinstance(attr, long):
            self.attr = attr
        else:
            attr = attr.upper()
            if attr == "TEXT":
                attr = "ORTH"
            if attr not in TOKEN_PATTERN_SCHEMA["items"]["properties"]:
                raise ValueError(Errors.E152.format(attr=attr))
            self.attr = self.vocab.strings[attr]

    def __len__(self):
        """Get the number of match IDs added to the matcher.

        RETURNS (int): The number of rules.

        DOCS: https://spacy.io/api/phrasematcher#len
        """
        return len(self._callbacks)

    def __contains__(self, key):
        """Check whether the matcher contains rules for a match ID.

        key (unicode): The match ID.
        RETURNS (bool): Whether the matcher contains rules for this match ID.

        DOCS: https://spacy.io/api/phrasematcher#contains
        """
        return key in self._callbacks

    def __reduce__(self):
        data = (self.vocab, self._docs, self._callbacks)
        return (unpickle_matcher, data, None, None)

    def remove(self, key):
        """Remove a match-rule from the matcher by match ID.

        key (unicode): The match ID.
        """
        if key not in self._keywords:
            return
        for keyword in self._keywords[key]:
            current_dict = self.keyword_trie_dict
            token_trie_list = []
            for tokens in keyword:
                if tokens in current_dict:
                    token_trie_list.append((tokens, current_dict))
                    current_dict = current_dict[tokens]
                else:
                    # if token is not found, break out of the loop
                    current_dict = None
                    break
            # remove the tokens from trie dict if there are no other
            # keywords with them
            if current_dict and self._terminal in current_dict:
                # if this is the only remaining key, remove unnecessary paths
                if current_dict[self._terminal] == [key]:
                    # we found a complete match for input keyword
                    token_trie_list.append((self._terminal, current_dict))
                    token_trie_list.reverse()
                    for key_to_remove, dict_pointer in token_trie_list:
                        if len(dict_pointer.keys()) == 1:
                            dict_pointer.pop(key_to_remove)
                        else:
                            # more than one key means more than 1 path,
                            # delete not required path and keep the other
                            dict_pointer.pop(key_to_remove)
                            break
                # otherwise simply remove the key
                else:
                    if key in current_dict[self._terminal]:
                        current_dict[self._terminal].remove(key)

        del self._keywords[key]
        del self._callbacks[key]
        del self._docs[key]

    def add(self, key, on_match, *docs):
        """Add a match-rule to the phrase-matcher. A match-rule consists of: an ID
        key, an on_match callback, and one or more patterns.

        key (unicode): The match ID.
        on_match (callable): Callback executed on match.
        *docs (Doc): `Doc` objects representing match patterns.

        DOCS: https://spacy.io/api/phrasematcher#add
        """

        _ = self.vocab[key]
        self._callbacks[key] = on_match
        self._keywords.setdefault(key, [])
        self._docs.setdefault(key, set())
        self._docs[key].update(docs)

        for doc in docs:
            if len(doc) == 0:
                continue
            if self.attr in (POS, TAG, LEMMA) and not doc.is_tagged:
                raise ValueError(Errors.E155.format())
            if self.attr == DEP and not doc.is_parsed:
                raise ValueError(Errors.E156.format())
            if self._validate and (doc.is_tagged or doc.is_parsed) \
              and self.attr not in (DEP, POS, TAG, LEMMA):
                string_attr = self.vocab.strings[self.attr]
                user_warning(Warnings.W012.format(key=key, attr=string_attr))
            keyword = self._convert_to_array(doc)
            # keep track of keywords per key to make remove easier
            # (would use a set, but can't hash numpy arrays)
            self._keywords[key].append(keyword)
            current_dict = self.keyword_trie_dict
            for token in keyword:
                current_dict = current_dict.setdefault(token, {})
            current_dict.setdefault(self._terminal, set())
            current_dict[self._terminal].add(key)

    def __call__(self, doc):
        """Find all sequences matching the supplied patterns on the `Doc`.

        doc (Doc): The document to match over.
        RETURNS (list): A list of `(key, start, end)` tuples,
            describing the matches. A match tuple describes a span
            `doc[start:end]`. The `label_id` and `key` are both integers.

        DOCS: https://spacy.io/api/phrasematcher#call
        """
        doc_array = self._convert_to_array(doc)
        matches = []
        if doc_array is None or len(doc_array) == 0:
            # if doc_array is empty or None just return empty list
            return matches
        current_dict = self.keyword_trie_dict
        start = 0
        reset_current_dict = False
        idx = 0
        doc_array_len = len(doc_array)
        while idx < doc_array_len:
            token = doc_array[idx]
            # if end is present in current_dict
            if self._terminal in current_dict or token in current_dict:
                if self._terminal in current_dict:
                    ent_id = current_dict[self._terminal]
                    matches.append((self.vocab.strings[ent_id], start, idx))

                # look for longer sequences from this position
                if token in current_dict:
                    current_dict_continued = current_dict[token]

                    idy = idx + 1
                    while idy < doc_array_len:
                        inner_token = doc_array[idy]
                        if self._terminal in current_dict_continued:
                            ent_ids = current_dict_continued[self._terminal]
                            for ent_id in ent_ids:
                                matches.append((self.vocab.strings[ent_id], start, idy))
                        if inner_token in current_dict_continued:
                            current_dict_continued = current_dict_continued[inner_token]
                        else:
                            break
                        idy += 1
                    else:
                        # end of doc_array reached
                        if self._terminal in current_dict_continued:
                            ent_ids = current_dict_continued[self._terminal]
                            for ent_id in ent_ids:
                                matches.append((self.vocab.strings[ent_id], start, idy))
                current_dict = self.keyword_trie_dict
                reset_current_dict = True
            else:
                # we reset current_dict
                current_dict = self.keyword_trie_dict
                reset_current_dict = True
            # if we are end of doc_array and have a sequence discovered
            if idx + 1 >= doc_array_len:
                if self._terminal in current_dict:
                    ent_ids = current_dict[self._terminal]
                    for ent_id in ent_ids:
                        matches.append((self.vocab.strings[ent_id], start, doc_array_len))
            idx += 1
            if reset_current_dict:
                reset_current_dict = False
                start = idx
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
        matcher_attr_string = "matcher:{}-{}".format(string_attr_name, string_attr_value)
        # Add new string to vocab
        _ = self.vocab[matcher_attr_string]
        return self.vocab.strings[matcher_attr_string]

    def _convert_to_array(self, Doc doc):
        return np.array([self.get_lex_value(doc, i) for i in range(len(doc))], dtype=np.uint64)


def unpickle_matcher(vocab, docs, callbacks):
    matcher = PhraseMatcher(vocab)
    for key, specs in docs.items():
        callback = callbacks.get(key, None)
        matcher.add(key, callback, *specs)
    return matcher

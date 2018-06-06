# coding: utf8
# cython: infer_types=True
# cython: bounds_check=False
# cython: profile=True
from __future__ import unicode_literals

from libc.string cimport memcpy, memset

from .doc cimport Doc, set_children_from_heads, token_by_start, token_by_end
from .span cimport Span
from .token cimport Token
from ..lexeme cimport Lexeme, EMPTY_LEXEME
from ..structs cimport LexemeC, TokenC
from ..attrs cimport TAG
from ..attrs import intify_attrs
from ..util import SimpleFrozenDict


cdef class Retokenizer:
    """Helper class for doc.retokenize() context manager."""
    cdef Doc doc
    cdef list merges
    cdef list splits
    def __init__(self, doc):
        self.doc = doc
        self.merges = []
        self.splits = []

    def merge(self, Span span, attrs=SimpleFrozenDict()):
        """Mark a span for merging. The attrs will be applied to the resulting
        token.
        """
        attrs = intify_attrs(attrs, strings_map=self.doc.vocab.strings)
        self.merges.append((span.start_char, span.end_char, attrs))

    def split(self, Token token, orths, attrs=SimpleFrozenDict()):
        """Mark a Token for splitting, into the specified orths. The attrs
        will be applied to each subtoken.
        """
        attrs = intify_attrs(attrs, strings_map=self.doc.vocab.strings)
        self.splits.append((token.start_char, orths, attrs))

    def __enter__(self):
        self.merges = []
        self.splits = []
        return self

    def __exit__(self, *args):
        # Do the actual merging here
        for start_char, end_char, attrs in self.merges:
            start = token_by_start(self.doc.c, self.doc.length, start_char)
            end = token_by_end(self.doc.c, self.doc.length, end_char)
            _merge(self.doc, start, end+1, attrs)
        for start_char, orths, attrs in self.splits:
            raise NotImplementedError


def _merge(Doc doc, int start, int end, attributes):
    """Retokenize the document, such that the span at
    `doc.text[start_idx : end_idx]` is merged into a single token. If
    `start_idx` and `end_idx `do not mark start and end token boundaries,
    the document remains unchanged.

    start_idx (int): Character index of the start of the slice to merge.
    end_idx (int): Character index after the end of the slice to merge.
    **attributes: Attributes to assign to the merged token. By default,
        attributes are inherited from the syntactic root of the span.
    RETURNS (Token): The newly merged token, or `None` if the start and end
        indices did not fall at token boundaries.
    """
    cdef Span span = doc[start:end]
    cdef int start_char = span.start_char
    cdef int end_char = span.end_char
    # Get LexemeC for newly merged token
    new_orth = ''.join([t.text_with_ws for t in span])
    if span[-1].whitespace_:
        new_orth = new_orth[:-len(span[-1].whitespace_)]
    cdef const LexemeC* lex = doc.vocab.get(doc.mem, new_orth)
    # House the new merged token where it starts
    cdef TokenC* token = &doc.c[start]
    token.spacy = doc.c[end-1].spacy
    for attr_name, attr_value in attributes.items():
        if attr_name == TAG:
            doc.vocab.morphology.assign_tag(token, attr_value)
        else:
            Token.set_struct_attr(token, attr_name, attr_value)
    # Make sure ent_iob remains consistent
    if doc.c[end].ent_iob == 1 and token.ent_iob in (0, 2):
        if token.ent_type == doc.c[end].ent_type:
            token.ent_iob = 3
        else:
            # If they're not the same entity type, let them be two entities
            doc.c[end].ent_iob = 3
    # Begin by setting all the head indices to absolute token positions
    # This is easier to work with for now than the offsets
    # Before thinking of something simpler, beware the case where a
    # dependency bridges over the entity. Here the alignment of the
    # tokens changes.
    span_root = span.root.i
    token.dep = span.root.dep
    # We update token.lex after keeping span root and dep, since
    # setting token.lex will change span.start and span.end properties
    # as it modifies the character offsets in the doc
    token.lex = lex
    for i in range(doc.length):
        doc.c[i].head += i
    # Set the head of the merged token, and its dep relation, from the Span
    token.head = doc.c[span_root].head
    # Adjust deps before shrinking tokens
    # Tokens which point into the merged token should now point to it
    # Subtract the offset from all tokens which point to >= end
    offset = (end - start) - 1
    for i in range(doc.length):
        head_idx = doc.c[i].head
        if start <= head_idx < end:
            doc.c[i].head = start
        elif head_idx >= end:
            doc.c[i].head -= offset
    # Now compress the token array
    for i in range(end, doc.length):
        doc.c[i - offset] = doc.c[i]
    for i in range(doc.length - offset, doc.length):
        memset(&doc.c[i], 0, sizeof(TokenC))
        doc.c[i].lex = &EMPTY_LEXEME
    doc.length -= offset
    for i in range(doc.length):
        # ...And, set heads back to a relative position
        doc.c[i].head -= i
    # Set the left/right children, left/right edges
    set_children_from_heads(doc.c, doc.length)
    # Clear the cached Python objects
    # Return the merged Python object
    return doc[start]

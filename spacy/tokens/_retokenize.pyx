# coding: utf8
# cython: infer_types=True
# cython: bounds_check=False
# cython: profile=True
from __future__ import unicode_literals

from libc.string cimport memcpy, memset
from libc.stdlib cimport malloc, free

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
        self.merges.append((span, attrs))

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
        _bulk_merge(self.doc, self.merges)
        for start_char, orths, attrs in self.splits:
            raise NotImplementedError


def _bulk_merge(Doc doc, merges):
    """Retokenize the document, such that the spans described in 'merges'
     are merged into a single token. This method assumes that the merges
     are in the same order at which they appear in the doc, and that merges
     do not intersect each other in any way.

    merges: Tokens to merge, and corresponding attributes to assign to the
        merged token. By default, attributes are inherited from the
        syntactic root of the span.
    RETURNS (Token): The first newly merged token.
    """
    cdef Span span
    cdef const LexemeC* lex
    cdef TokenC* token
    spans = []
    cdef TokenC** tokens = <TokenC **>malloc(len(merges) * sizeof(TokenC))

    try:
        for merge_index, (span, attributes) in enumerate(merges):
            start = span.start
            end = span.end
            spans.append(span)

            # House the new merged token where it starts
            token = &doc.c[start]

            tokens[merge_index] = token

            # Assign attributes
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

        # Memorize span roots and sets dependencies of the newly merged
        # tokens to the dependencies of their roots.
        span_roots = []
        for i, span in enumerate(spans):
            span_roots.append(span.root.i)
            tokens[i].dep = span.root.dep

        # We update token.lex after keeping span root and dep, since
        # setting token.lex will change span.start and span.end properties
        # as it modifies the character offsets in the doc
        for token_index in range(len(merges)):
            new_orth = ''.join([t.text_with_ws for t in spans[token_index]])
            if spans[token_index][-1].whitespace_:
                new_orth = new_orth[:-len(spans[token_index][-1].whitespace_)]
            lex = doc.vocab.get(doc.mem, new_orth)
            tokens[token_index].lex = lex
            # We set trailing space here too
            tokens[token_index].spacy = doc.c[spans[token_index].end-1].spacy

        # Begin by setting all the head indices to absolute token positions
        # This is easier to work with for now than the offsets
        # Before thinking of something simpler, beware the case where a
        # dependency bridges over the entity. Here the alignment of the
        # tokens changes.
        for i in range(doc.length):
            doc.c[i].head += i

        # Set the head of the merged token from the Span
        for i in range(len(merges)):
            tokens[i].head = doc.c[span_roots[i]].head

        # Adjust deps before shrinking tokens
        # Tokens which point into the merged token should now point to it
        # Subtract the offset from all tokens which point to >= end
        offsets = []
        current_span_index = 0
        current_offset = 0
        for i in range(doc.length):
            if current_span_index < len(spans) and i == spans[current_span_index].end:
                #last token was the last of the span
                current_offset += (spans[current_span_index].end - spans[current_span_index].start) -1
                current_span_index += 1

            if current_span_index < len(spans) and\
                    spans[current_span_index].start <= i < spans[current_span_index].end:
                offsets.append(spans[current_span_index].start - current_offset)
            else:
                offsets.append(i - current_offset)


        for i in range(doc.length):
            doc.c[i].head = offsets[doc.c[i].head]

        # Now compress the token array
        offset = 0
        in_span = False
        span_index = 0
        for i in range(doc.length):
            if in_span and i == spans[span_index].end:
                # First token after a span
                in_span = False
                span_index += 1
            if span_index < len(spans) and i == spans[span_index].start:
                # First token in a span
                doc.c[i - offset] = doc.c[i] # move token to its place
                offset += (spans[span_index].end - spans[span_index].start) - 1
                in_span = True
            if not in_span:
                doc.c[i - offset] = doc.c[i] # move token to its place

        for i in range(doc.length - offset, doc.length):
            memset(&doc.c[i], 0, sizeof(TokenC))
            doc.c[i].lex = &EMPTY_LEXEME
        doc.length -= offset

        # ...And, set heads back to a relative position
        for i in range(doc.length):
            doc.c[i].head -= i

        # Set the left/right children, left/right edges
        set_children_from_heads(doc.c, doc.length)

    finally:
        free(tokens)
    # Return the merged Python object
    return doc[spans[0].start]

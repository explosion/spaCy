# coding: utf8
# cython: infer_types=True
# cython: bounds_check=False
# cython: profile=True
from __future__ import unicode_literals

from libc.string cimport memcpy, memset
from libc.stdlib cimport malloc, free
from cymem.cymem cimport Pool
from thinc.neural.util import get_array_module

import numpy

from .doc cimport Doc, set_children_from_heads, token_by_start, token_by_end
from .span cimport Span
from .token cimport Token
from ..lexeme cimport Lexeme, EMPTY_LEXEME
from ..structs cimport LexemeC, TokenC
from ..attrs cimport TAG

from .underscore import is_writable_attr
from ..attrs import intify_attrs
from ..util import SimpleFrozenDict
from ..errors import Errors
from ..strings import get_string_id


cdef class Retokenizer:
    """Helper class for doc.retokenize() context manager.

    DOCS: https://spacy.io/api/doc#retokenize
    USAGE: https://spacy.io/usage/linguistic-features#retokenization
    """
    cdef Doc doc
    cdef list merges
    cdef list splits
    cdef set tokens_to_merge

    def __init__(self, doc):
        self.doc = doc
        self.merges = []
        self.splits = []
        self.tokens_to_merge = set()

    def merge(self, Span span, attrs=SimpleFrozenDict()):
        """Mark a span for merging. The attrs will be applied to the resulting
        token.

        span (Span): The span to merge.
        attrs (dict): Attributes to set on the merged token.

        DOCS: https://spacy.io/api/doc#retokenizer.merge
        """
        for token in span:
            if token.i in self.tokens_to_merge:
                raise ValueError(Errors.E102.format(token=repr(token)))
            self.tokens_to_merge.add(token.i)
        if "_" in attrs:  # Extension attributes
            extensions = attrs["_"]
            _validate_extensions(extensions)
            attrs = {key: value for key, value in attrs.items() if key != "_"}
            attrs = intify_attrs(attrs, strings_map=self.doc.vocab.strings)
            attrs["_"] = extensions
        else:
            attrs = intify_attrs(attrs, strings_map=self.doc.vocab.strings)
        self.merges.append((span, attrs))

    def split(self, Token token, orths, heads, attrs=SimpleFrozenDict()):
        """Mark a Token for splitting, into the specified orths. The attrs
        will be applied to each subtoken.

        token (Token): The token to split.
        orths (list): The verbatim text of the split tokens. Needs to match the
            text of the original token.
        heads (list): List of token or `(token, subtoken)` tuples specifying the
            tokens to attach the newly split subtokens to.
        attrs (dict): Attributes to set on all split tokens. Attribute names
            mapped to list of per-token attribute values.

        DOCS: https://spacy.io/api/doc#retokenizer.split
        """
        if ''.join(orths) != token.text:
            raise ValueError(Errors.E117.format(new=''.join(orths), old=token.text))
        if "_" in attrs:  # Extension attributes
            extensions = attrs["_"]
            for extension in extensions:
                _validate_extensions(extension)
            attrs = {key: value for key, value in attrs.items() if key != "_"}
            # NB: Since we support {"KEY": [value, value]} syntax here, this
            # will only "intify" the keys, not the values
            attrs = intify_attrs(attrs, strings_map=self.doc.vocab.strings)
            attrs["_"] = extensions
        else:
            # NB: Since we support {"KEY": [value, value]} syntax here, this
            # will only "intify" the keys, not the values
            attrs = intify_attrs(attrs, strings_map=self.doc.vocab.strings)
        head_offsets = []
        for head in heads:
            if isinstance(head, Token):
                head_offsets.append((head.idx, 0))
            else:
                head_offsets.append((head[0].idx, head[1]))
        self.splits.append((token.idx, orths, head_offsets, attrs))

    def __enter__(self):
        self.merges = []
        self.splits = []
        return self

    def __exit__(self, *args):
        # Do the actual merging here
        if len(self.merges) > 1:
            _bulk_merge(self.doc, self.merges)
        elif len(self.merges) == 1:
            (span, attrs) = self.merges[0]
            start = span.start
            end = span.end
            _merge(self.doc, start, end, attrs)
        # Iterate in order, to keep things simple.
        for start_char, orths, heads, attrs in sorted(self.splits):
            # Resolve token index
            token_index = token_by_start(self.doc.c, self.doc.length, start_char)
            # Check we're still able to find tokens starting at the character offsets
            # referred to in the splits. If we merged these tokens previously, we
            # have to raise an error
            if token_index == -1:
                raise IndexError(Errors.E122)
            head_indices = []
            for head_char, subtoken in heads:
                head_index = token_by_start(self.doc.c, self.doc.length, head_char)
                if head_index == -1:
                    raise IndexError(Errors.E123)
                # We want to refer to the token index of the head *after* the
                # mergery. We need to account for the extra tokens introduced.
                # e.g., let's say we have [ab, c] and we want a and b to depend
                # on c. The correct index for c will be 2, not 1.
                if head_index > token_index:
                    head_index += len(orths)-1
                head_indices.append(head_index+subtoken)
            _split(self.doc, token_index, orths, head_indices, attrs)


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
    # Resize the doc.tensor, if it's set. Let the last row for each token stand
    # for the merged region. To do this, we create a boolean array indicating
    # whether the row is to be deleted, then use numpy.delete
    if doc.tensor is not None and doc.tensor.size != 0:
        doc.tensor = _resize_tensor(doc.tensor, [(start, end)])
    # Get LexemeC for newly merged token
    new_orth = ''.join([t.text_with_ws for t in span])
    if span[-1].whitespace_:
        new_orth = new_orth[:-len(span[-1].whitespace_)]
    cdef const LexemeC* lex = doc.vocab.get(doc.mem, new_orth)
    # House the new merged token where it starts
    cdef TokenC* token = &doc.c[start]
    token.spacy = doc.c[end-1].spacy
    for attr_name, attr_value in attributes.items():
        if attr_name == "_":  # Set extension attributes
            for ext_attr_key, ext_attr_value in attr_value.items():
                doc[start]._.set(ext_attr_key, ext_attr_value)
        elif attr_name == TAG:
            doc.vocab.morphology.assign_tag(token, attr_value)
        else:
            # Set attributes on both token and lexeme to take care of token
            # attribute vs. lexical attribute without having to enumerate them.
            # If an attribute name is not valid, set_struct_attr will ignore it.
            Token.set_struct_attr(token, attr_name, attr_value)
            Lexeme.set_struct_attr(<LexemeC*>lex, attr_name, attr_value)
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
    # Return the merged Python object
    return doc[start]


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
    cdef Pool mem = Pool()
    tokens = <TokenC**>mem.alloc(len(merges), sizeof(TokenC))
    spans = []

    def _get_start(merge):
        return merge[0].start

    merges.sort(key=_get_start)
    for merge_index, (span, attributes) in enumerate(merges):
        start = span.start
        end = span.end
        spans.append(span)
        # House the new merged token where it starts
        token = &doc.c[start]
        tokens[merge_index] = token
    # Resize the doc.tensor, if it's set. Let the last row for each token stand
    # for the merged region. To do this, we create a boolean array indicating
    # whether the row is to be deleted, then use numpy.delete
    if doc.tensor is not None and doc.tensor.size != 0:
        doc.tensor = _resize_tensor(doc.tensor,
            [(m[0].start, m[0].end) for m in merges])
    # Memorize span roots and sets dependencies of the newly merged
    # tokens to the dependencies of their roots.
    span_roots = []
    for i, span in enumerate(spans):
        span_roots.append(span.root.i)
        tokens[i].dep = span.root.dep
    # We update token.lex after keeping span root and dep, since
    # setting token.lex will change span.start and span.end properties
    # as it modifies the character offsets in the doc
    for token_index, (span, attributes) in enumerate(merges):
        new_orth = ''.join([t.text_with_ws for t in spans[token_index]])
        if spans[token_index][-1].whitespace_:
            new_orth = new_orth[:-len(spans[token_index][-1].whitespace_)]
        token = tokens[token_index]
        lex = doc.vocab.get(doc.mem, new_orth)
        token.lex = lex
        # We set trailing space here too
        token.spacy = doc.c[spans[token_index].end-1].spacy
        py_token = span[0]
        # Assign attributes
        for attr_name, attr_value in attributes.items():
            if attr_name == "_":  # Set extension attributes
                for ext_attr_key, ext_attr_value in attr_value.items():
                    py_token._.set(ext_attr_key, ext_attr_value)
            elif attr_name == TAG:
                doc.vocab.morphology.assign_tag(token, attr_value)
            else:
                # Set attributes on both token and lexeme to take care of token
                # attribute vs. lexical attribute without having to enumerate
                # them. If an attribute name is not valid, set_struct_attr will
                # ignore it.
                Token.set_struct_attr(token, attr_name, attr_value)
                Lexeme.set_struct_attr(<LexemeC*>lex, attr_name, attr_value)
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
            # Last token was the last of the span
            current_offset += (spans[current_span_index].end - spans[current_span_index].start) -1
            current_span_index += 1
        if current_span_index < len(spans) and \
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
    # Make sure ent_iob remains consistent
    for (span, _) in merges:
        if(span.end < len(offsets)):
        # If it's not the last span
            token_after_span_position = offsets[span.end]
            if doc.c[token_after_span_position].ent_iob == 1\
                    and doc.c[token_after_span_position - 1].ent_iob in (0, 2):
                if doc.c[token_after_span_position - 1].ent_type == doc.c[token_after_span_position].ent_type:
                    doc.c[token_after_span_position - 1].ent_iob = 3
                else:
                    # If they're not the same entity type, let them be two entities
                    doc.c[token_after_span_position].ent_iob = 3
    # Return the merged Python object
    return doc[spans[0].start]


def _resize_tensor(tensor, ranges):
    delete = []
    for start, end in ranges:
        for i in range(start, end-1):
            delete.append(i)
    xp = get_array_module(tensor)
    return xp.delete(tensor, delete, axis=0)


def _split(Doc doc, int token_index, orths, heads, attrs):
    """Retokenize the document, such that the token at
    `doc[token_index]` is split into tokens with the orth 'orths'
    token_index(int): token index of the token to split.
    orths: IDs of the verbatim text content of the tokens to create
    **attributes: Attributes to assign to each of the newly created tokens. By default,
        attributes are inherited from the original token.
    RETURNS (Token): The first newly created token.
    """
    cdef int nb_subtokens = len(orths)
    cdef const LexemeC* lex
    cdef TokenC* token
    cdef TokenC orig_token = doc.c[token_index]

    if(len(heads) != nb_subtokens):
        raise ValueError(Errors.E115)
    # First, make the dependencies absolutes
    for i in range(doc.length):
        doc.c[i].head += i
    # Adjust dependencies, so they refer to post-split indexing
    offset = nb_subtokens - 1
    for i in range(doc.length):
        if doc.c[i].head > token_index:
            doc.c[i].head += offset
    # Double doc.c max_length if necessary (until big enough for all new tokens)
    while doc.length + nb_subtokens - 1 >= doc.max_length:
        doc._realloc(doc.length * 2)
    # Move tokens after the split to create space for the new tokens
    doc.length = len(doc) + nb_subtokens -1
    for token_to_move in range(doc.length - 1, token_index, -1):
        doc.c[token_to_move + nb_subtokens - 1] = doc.c[token_to_move]
    # Host the tokens in the newly created space
    cdef int idx_offset = 0
    for i, orth in enumerate(orths):
        token = &doc.c[token_index + i]
        lex = doc.vocab.get(doc.mem, orth)
        token.lex = lex
        # Update the character offset of the subtokens
        if i != 0:
            token.idx = orig_token.idx + idx_offset
        idx_offset += len(orth)
        # Set token.spacy to False for all non-last split tokens, and
        # to origToken.spacy for the last token
        if (i < nb_subtokens - 1):
            token.spacy = False
        else:
            token.spacy = orig_token.spacy
        # Make IOB consistent
        if (orig_token.ent_iob == 3):
            if i == 0:
                token.ent_iob = 3
            else:
                token.ent_iob = 1
        else:
            # In all other cases subtokens inherit iob from origToken
            token.ent_iob = orig_token.ent_iob
    # Apply attrs to each subtoken
    for attr_name, attr_values in attrs.items():
        for i, attr_value in enumerate(attr_values):
            token = &doc.c[token_index + i]
            if attr_name == "_":
                for ext_attr_key, ext_attr_value in attr_value.items():
                    doc[token_index + i]._.set(ext_attr_key, ext_attr_value)
            # NB: We need to call get_string_id here because only the keys are
            # "intified" (since we support "KEY": [value, value] syntax here).
            elif attr_name == TAG:
                doc.vocab.morphology.assign_tag(token, get_string_id(attr_value))
            else:
                # Set attributes on both token and lexeme to take care of token
                # attribute vs. lexical attribute without having to enumerate
                # them. If an attribute name is not valid, set_struct_attr will
                # ignore it.
                Token.set_struct_attr(token, attr_name, get_string_id(attr_value))
                Lexeme.set_struct_attr(<LexemeC*>token.lex, attr_name, get_string_id(attr_value))
    # Assign correct dependencies to the inner token
    for i, head in enumerate(heads):
        doc.c[token_index + i].head = head
    # Transform the dependencies into relative ones again
    for i in range(doc.length):
        doc.c[i].head -= i
    # set children from head
    set_children_from_heads(doc.c, doc.length)


def _validate_extensions(extensions):
    if not isinstance(extensions, dict):
        raise ValueError(Errors.E120.format(value=repr(extensions)))
    for key, value in extensions.items():
        # Get the extension and make sure it's available and writable
        extension = Token.get_extension(key)
        if not extension:  # Extension attribute doesn't exist
            raise ValueError(Errors.E118.format(attr=key))
        if not is_writable_attr(extension):
            raise ValueError(Errors.E119.format(attr=key))

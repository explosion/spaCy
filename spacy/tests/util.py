# coding: utf-8
from __future__ import unicode_literals

from ..tokens import Doc
from ..attrs import ORTH, POS, HEAD, DEP

import numpy


def get_doc(vocab, words=[], pos=None, heads=None, deps=None, tags=None, ents=None):
    """Create Doc object from given vocab, words and annotations."""
    pos = pos or [''] * len(words)
    heads = heads or [0] * len(words)
    deps = deps or [''] * len(words)

    doc = Doc(vocab, words=words)
    attrs = doc.to_array([POS, HEAD, DEP])
    for i, (p, head, dep) in enumerate(zip(pos, heads, deps)):
        attrs[i, 0] = doc.vocab.strings[p]
        attrs[i, 1] = head
        attrs[i, 2] = doc.vocab.strings[dep]
    doc.from_array([POS, HEAD, DEP], attrs)
    if ents:
        doc.ents = [(ent_id, doc.vocab.strings[label], start, end) for ent_id, label, start, end in ents]
    if tags:
        for token in doc:
            token.tag_ = tags[token.i]
    return doc


def apply_transition_sequence(parser, doc, sequence):
    """Perform a series of pre-specified transitions, to put the parser in a
    desired state."""
    for action_name in sequence:
        if '-' in action_name:
            move, label = action_name.split('-')
            parser.add_label(label)
    with parser.step_through(doc) as stepwise:
        for transition in sequence:
            stepwise.transition(transition)


def add_vecs_to_vocab(vocab, vectors):
    """Add list of vector tuples to given vocab. All vectors need to have the
    same length. Format: [("text", [1, 2, 3])]"""
    length = len(vectors[0][1])
    vocab.resize_vectors(length)
    for word, vec in vectors:
        vocab[word].vector = vec
    return vocab


def get_cosine(vec1, vec2):
    """Get cosine for two given vectors"""
    return numpy.dot(vec1, vec2) / (numpy.linalg.norm(vec1) * numpy.linalg.norm(vec2))


def assert_docs_equal(doc1, doc2):
    """Compare two Doc objects and assert that they're equal. Tests for tokens,
    tags, dependencies and entities."""
    assert [ t.orth for t in doc1 ] == [ t.orth for t in doc2 ]

    assert [ t.pos for t in doc1 ] == [ t.pos for t in doc2 ]
    assert [ t.tag for t in doc1 ] == [ t.tag for t in doc2 ]

    assert [ t.head.i for t in doc1 ] == [ t.head.i for t in doc2 ]
    assert [ t.dep for t in doc1 ] == [ t.dep for t in doc2 ]
    if doc1.is_parsed and doc2.is_parsed:
        assert [ s for s in doc1.sents ] == [ s for s in doc2.sents ]

    assert [ t.ent_type for t in doc1 ] == [ t.ent_type for t in doc2 ]
    assert [ t.ent_iob for t in doc1 ] == [ t.ent_iob for t in doc2 ]
    assert [ ent for ent in doc1.ents ] == [ ent for ent in doc2.ents ]

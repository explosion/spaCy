# coding: utf-8
from __future__ import unicode_literals

from ..tokens import Doc
from ..attrs import ORTH, POS, HEAD, DEP
from ..compat import path2str

import pytest
import numpy
import tempfile
import shutil
import contextlib
import msgpack
from pathlib import Path


MODELS = {}


def load_test_model(model):
    """Load a model if it's installed as a package, otherwise skip."""
    if model not in MODELS:
        module = pytest.importorskip(model)
        MODELS[model] = module.load()
    return MODELS[model]


@contextlib.contextmanager
def make_tempfile(mode='r'):
    f = tempfile.TemporaryFile(mode=mode)
    yield f
    f.close()


@contextlib.contextmanager
def make_tempdir():
    d = Path(tempfile.mkdtemp())
    yield d
    shutil.rmtree(path2str(d))


def get_doc(vocab, words=[], pos=None, heads=None, deps=None, tags=None, ents=None):
    """Create Doc object from given vocab, words and annotations."""
    pos = pos or [''] * len(words)
    tags = tags or [''] * len(words)
    heads = heads or [0] * len(words)
    deps = deps or [''] * len(words)
    for value in (deps+tags+pos):
        vocab.strings.add(value)

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
    vocab.reset_vectors(width=length)
    for word, vec in vectors:
        vocab.set_vector(word, vector=vec)
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


def assert_packed_msg_equal(b1, b2):
    """Assert that two packed msgpack messages are equal."""
    msg1 = msgpack.loads(b1, encoding='utf8')
    msg2 = msgpack.loads(b2, encoding='utf8')
    assert sorted(msg1.keys()) == sorted(msg2.keys())
    for (k1, v1), (k2, v2) in zip(sorted(msg1.items()), sorted(msg2.items())):
        assert k1 == k2
        assert v1 == v2

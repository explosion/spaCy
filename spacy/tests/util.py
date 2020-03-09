# coding: utf-8
from __future__ import unicode_literals

import numpy
import tempfile
import shutil
import contextlib
import srsly
from pathlib import Path

from spacy import Errors
from spacy.tokens import Doc, Span
from spacy.attrs import POS, TAG, HEAD, DEP, LEMMA
from spacy.compat import path2str


@contextlib.contextmanager
def make_tempfile(mode="r"):
    f = tempfile.TemporaryFile(mode=mode)
    yield f
    f.close()


@contextlib.contextmanager
def make_tempdir():
    d = Path(tempfile.mkdtemp())
    yield d
    shutil.rmtree(path2str(d))


def get_doc(vocab, words=[], pos=None, heads=None, deps=None, tags=None, ents=None, lemmas=None):
    """Create Doc object from given vocab, words and annotations."""
    if deps and not heads:
        heads = [0] * len(deps)
    headings = []
    values = []
    annotations = [pos, heads, deps, lemmas, tags]
    possible_headings = [POS, HEAD, DEP, LEMMA, TAG]
    for a, annot in enumerate(annotations):
        if annot is not None:
            if len(annot) != len(words):
                raise ValueError(Errors.E189)
            headings.append(possible_headings[a])
            if annot is not heads:
                values.extend(annot)
    for value in values:
        vocab.strings.add(value)

    doc = Doc(vocab, words=words)

    # if there are any other annotations, set them
    if headings:
        attrs = doc.to_array(headings)

        j = 0
        for annot in annotations:
            if annot:
                if annot is heads:
                    for i in range(len(words)):
                        if attrs.ndim == 1:
                            attrs[i] = heads[i]
                        else:
                            attrs[i,j] = heads[i]
                else:
                    for i in range(len(words)):
                        if attrs.ndim == 1:
                            attrs[i] = doc.vocab.strings[annot[i]]
                        else:
                            attrs[i, j] = doc.vocab.strings[annot[i]]
                j += 1
        doc.from_array(headings, attrs)

    # finally, set the entities
    if ents:
        doc.ents = [
            Span(doc, start, end, label=doc.vocab.strings[label])
            for start, end, label in ents
        ]
    return doc


def apply_transition_sequence(parser, doc, sequence):
    """Perform a series of pre-specified transitions, to put the parser in a
    desired state."""
    for action_name in sequence:
        if "-" in action_name:
            move, label = action_name.split("-")
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
    assert [t.orth for t in doc1] == [t.orth for t in doc2]

    assert [t.pos for t in doc1] == [t.pos for t in doc2]
    assert [t.tag for t in doc1] == [t.tag for t in doc2]

    assert [t.head.i for t in doc1] == [t.head.i for t in doc2]
    assert [t.dep for t in doc1] == [t.dep for t in doc2]
    if doc1.is_parsed and doc2.is_parsed:
        assert [s for s in doc1.sents] == [s for s in doc2.sents]

    assert [t.ent_type for t in doc1] == [t.ent_type for t in doc2]
    assert [t.ent_iob for t in doc1] == [t.ent_iob for t in doc2]
    for ent1, ent2 in zip(doc1.ents, doc2.ents):
        assert ent1.start == ent2.start
        assert ent1.end == ent2.end
        assert ent1.label == ent2.label
        assert ent1.kb_id == ent2.kb_id


def assert_packed_msg_equal(b1, b2):
    """Assert that two packed msgpack messages are equal."""
    msg1 = srsly.msgpack_loads(b1)
    msg2 = srsly.msgpack_loads(b2)
    assert sorted(msg1.keys()) == sorted(msg2.keys())
    for (k1, v1), (k2, v2) in zip(sorted(msg1.items()), sorted(msg2.items())):
        assert k1 == k2
        assert v1 == v2

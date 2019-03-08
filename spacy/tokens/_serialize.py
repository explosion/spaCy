# coding: utf8
from __future__ import unicode_literals

import numpy
import gzip
import srsly
from thinc.neural.ops import NumpyOps

from ..compat import copy_reg
from ..tokens import Doc
from ..attrs import SPACY, ORTH


class Binder(object):
    """Serialize analyses from a collection of doc objects."""

    def __init__(self, attrs=None):
        """Create a Binder object, to hold serialized annotations.

        attrs (list): List of attributes to serialize. 'orth' and 'spacy' are
            always serialized, so they're not required. Defaults to None.
        """
        attrs = attrs or []
        self.attrs = list(attrs)
        # Ensure ORTH is always attrs[0]
        if ORTH in self.attrs:
            self.attrs.pop(ORTH)
        if SPACY in self.attrs:
            self.attrs.pop(SPACY)
        self.attrs.insert(0, ORTH)
        self.tokens = []
        self.spaces = []
        self.strings = set()

    def add(self, doc):
        """Add a doc's annotations to the binder for serialization."""
        array = doc.to_array(self.attrs)
        if len(array.shape) == 1:
            array = array.reshape((array.shape[0], 1))
        self.tokens.append(array)
        spaces = doc.to_array(SPACY)
        assert array.shape[0] == spaces.shape[0]
        spaces = spaces.reshape((spaces.shape[0], 1))
        self.spaces.append(numpy.asarray(spaces, dtype=bool))
        self.strings.update(w.text for w in doc)

    def get_docs(self, vocab):
        """Recover Doc objects from the annotations, using the given vocab."""
        for string in self.strings:
            vocab[string]
        orth_col = self.attrs.index(ORTH)
        for tokens, spaces in zip(self.tokens, self.spaces):
            words = [vocab.strings[orth] for orth in tokens[:, orth_col]]
            doc = Doc(vocab, words=words, spaces=spaces)
            doc = doc.from_array(self.attrs, tokens)
            yield doc

    def merge(self, other):
        """Extend the annotations of this binder with the annotations from another."""
        assert self.attrs == other.attrs
        self.tokens.extend(other.tokens)
        self.spaces.extend(other.spaces)
        self.strings.update(other.strings)

    def to_bytes(self):
        """Serialize the binder's annotations into a byte string."""
        for tokens in self.tokens:
            assert len(tokens.shape) == 2, tokens.shape
        lengths = [len(tokens) for tokens in self.tokens]
        msg = {
            "attrs": self.attrs,
            "tokens": numpy.vstack(self.tokens).tobytes("C"),
            "spaces": numpy.vstack(self.spaces).tobytes("C"),
            "lengths": numpy.asarray(lengths, dtype="int32").tobytes("C"),
            "strings": list(self.strings),
        }
        return gzip.compress(srsly.msgpack_dumps(msg))

    def from_bytes(self, string):
        """Deserialize the binder's annotations from a byte string."""
        msg = srsly.msgpack_loads(gzip.decompress(string))
        self.attrs = msg["attrs"]
        self.strings = set(msg["strings"])
        lengths = numpy.fromstring(msg["lengths"], dtype="int32")
        flat_spaces = numpy.fromstring(msg["spaces"], dtype=bool)
        flat_tokens = numpy.fromstring(msg["tokens"], dtype="uint64")
        shape = (flat_tokens.size // len(self.attrs), len(self.attrs))
        flat_tokens = flat_tokens.reshape(shape)
        flat_spaces = flat_spaces.reshape((flat_spaces.size, 1))
        self.tokens = NumpyOps().unflatten(flat_tokens, lengths)
        self.spaces = NumpyOps().unflatten(flat_spaces, lengths)
        for tokens in self.tokens:
            assert len(tokens.shape) == 2, tokens.shape
        return self


def merge_bytes(binder_strings):
    """Concatenate multiple serialized binders into one byte string."""
    output = None
    for byte_string in binder_strings:
        binder = Binder().from_bytes(byte_string)
        if output is None:
            output = binder
        else:
            output.merge(binder)
    return output.to_bytes()


def pickle_binder(binder):
    return (unpickle_binder, (binder.to_bytes(),))


def unpickle_binder(byte_string):
    return Binder().from_bytes(byte_string)


copy_reg.pickle(Binder, pickle_binder, unpickle_binder)

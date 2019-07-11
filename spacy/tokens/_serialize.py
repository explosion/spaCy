# coding: utf8
from __future__ import unicode_literals

import numpy
import gzip
import srsly
from thinc.neural.ops import NumpyOps

from ..compat import copy_reg
from ..tokens import Doc
from ..attrs import SPACY, ORTH


class DocBox(object):
    """Serialize analyses from a collection of doc objects."""

    def __init__(self, attrs=None, store_user_data=False):
        """Create a DocBox object, to hold serialized annotations.

        attrs (list): List of attributes to serialize. 'orth' and 'spacy' are
            always serialized, so they're not required. Defaults to None.
        """
        attrs = attrs or []
        # Ensure ORTH is always attrs[0]
        self.attrs = [attr for attr in attrs if attr != ORTH and attr != SPACY]
        self.attrs.insert(0, ORTH)
        self.tokens = []
        self.spaces = []
        self.user_data = []
        self.strings = set()
        self.store_user_data = store_user_data

    def add(self, doc):
        """Add a doc's annotations to the DocBox for serialization."""
        array = doc.to_array(self.attrs)
        if len(array.shape) == 1:
            array = array.reshape((array.shape[0], 1))
        self.tokens.append(array)
        spaces = doc.to_array(SPACY)
        assert array.shape[0] == spaces.shape[0]
        spaces = spaces.reshape((spaces.shape[0], 1))
        self.spaces.append(numpy.asarray(spaces, dtype=bool))
        self.strings.update(w.text for w in doc)
        if self.store_user_data:
            self.user_data.append(srsly.msgpack_dumps(doc.user_data))

    def get_docs(self, vocab):
        """Recover Doc objects from the annotations, using the given vocab."""
        for string in self.strings:
            vocab[string]
        orth_col = self.attrs.index(ORTH)
        for i in range(len(self.tokens)):
            tokens = self.tokens[i]
            spaces = self.spaces[i]
            words = [vocab.strings[orth] for orth in tokens[:, orth_col]]
            doc = Doc(vocab, words=words, spaces=spaces)
            doc = doc.from_array(self.attrs, tokens)
            if self.store_user_data:
                doc.user_data.update(srsly.msgpack_loads(self.user_data[i]))
            yield doc

    def merge(self, other):
        """Extend the annotations of this DocBox with the annotations from another."""
        assert self.attrs == other.attrs
        self.tokens.extend(other.tokens)
        self.spaces.extend(other.spaces)
        self.strings.update(other.strings)
        if self.store_user_data:
            self.user_data.extend(other.user_data)

    def to_bytes(self):
        """Serialize the DocBox's annotations into a byte string."""
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
        if self.store_user_data:
            msg["user_data"] = self.user_data
        return gzip.compress(srsly.msgpack_dumps(msg))

    def from_bytes(self, string):
        """Deserialize the DocBox's annotations from a byte string."""
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
        if self.store_user_data and "user_data" in msg:
            self.user_data = list(msg["user_data"])
        for tokens in self.tokens:
            assert len(tokens.shape) == 2, tokens.shape
        return self


def merge_boxes(boxes):
    merged = None
    for byte_string in boxes:
        if byte_string is not None:
            box = DocBox(store_user_data=True).from_bytes(byte_string)
            if merged is None:
                merged = box
            else:
                merged.merge(box)
    if merged is not None:
        return merged.to_bytes()
    else:
        return b""


def pickle_box(box):
    return (unpickle_box, (box.to_bytes(),))


def unpickle_box(byte_string):
    return DocBox().from_bytes(byte_string)


copy_reg.pickle(DocBox, pickle_box, unpickle_box)
# Compatibility, as we had named it this previously.
Binder = DocBox

__all__ = ["DocBox"]

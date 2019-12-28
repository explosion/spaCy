# coding: utf8
from __future__ import unicode_literals

import numpy
import zlib
import srsly
from thinc.neural.ops import NumpyOps

from ..compat import copy_reg
from ..tokens import Doc
from ..attrs import SPACY, ORTH, intify_attr
from ..errors import Errors


class DocBin(object):
    """Pack Doc objects for binary serialization.

    The DocBin class lets you efficiently serialize the information from a
    collection of Doc objects. You can control which information is serialized
    by passing a list of attribute IDs, and optionally also specify whether the
    user data is serialized. The DocBin is faster and produces smaller data
    sizes than pickle, and allows you to deserialize without executing arbitrary
    Python code.

    The serialization format is gzipped msgpack, where the msgpack object has
    the following structure:

    {
        "attrs": List[uint64], # e.g. [TAG, HEAD, ENT_IOB, ENT_TYPE]
        "tokens": bytes, # Serialized numpy uint64 array with the token data
        "spaces": bytes, # Serialized numpy boolean array with spaces data
        "lengths": bytes, # Serialized numpy int32 array with the doc lengths
        "strings": List[unicode] # List of unique strings in the token data
    }

    Strings for the words, tags, labels etc are represented by 64-bit hashes in
    the token data, and every string that occurs at least once is passed via the
    strings object. This means the storage is more efficient if you pack more
    documents together, because you have less duplication in the strings.

    A notable downside to this format is that you can't easily extract just one
    document from the DocBin.
    """

    def __init__(self, attrs=None, store_user_data=False):
        """Create a DocBin object to hold serialized annotations.

        attrs (list): List of attributes to serialize. 'orth' and 'spacy' are
            always serialized, so they're not required. Defaults to None.
        store_user_data (bool): Whether to include the `Doc.user_data`.
        RETURNS (DocBin): The newly constructed object.

        DOCS: https://spacy.io/api/docbin#init
        """
        attrs = attrs or []
        attrs = sorted([intify_attr(attr) for attr in attrs])
        self.attrs = [attr for attr in attrs if attr != ORTH and attr != SPACY]
        self.attrs.insert(0, ORTH)  # Ensure ORTH is always attrs[0]
        self.tokens = []
        self.spaces = []
        self.cats = []
        self.user_data = []
        self.strings = set()
        self.store_user_data = store_user_data

    def __len__(self):
        """RETURNS: The number of Doc objects added to the DocBin."""
        return len(self.tokens)

    def add(self, doc):
        """Add a Doc's annotations to the DocBin for serialization.

        doc (Doc): The Doc object to add.

        DOCS: https://spacy.io/api/docbin#add
        """
        array = doc.to_array(self.attrs)
        if len(array.shape) == 1:
            array = array.reshape((array.shape[0], 1))
        self.tokens.append(array)
        spaces = doc.to_array(SPACY)
        assert array.shape[0] == spaces.shape[0]  # this should never happen
        spaces = spaces.reshape((spaces.shape[0], 1))
        self.spaces.append(numpy.asarray(spaces, dtype=bool))
        self.strings.update(w.text for w in doc)
        self.cats.append(doc.cats)
        if self.store_user_data:
            self.user_data.append(srsly.msgpack_dumps(doc.user_data))

    def get_docs(self, vocab):
        """Recover Doc objects from the annotations, using the given vocab.

        vocab (Vocab): The shared vocab.
        YIELDS (Doc): The Doc objects.

        DOCS: https://spacy.io/api/docbin#get_docs
        """
        for string in self.strings:
            vocab[string]
        orth_col = self.attrs.index(ORTH)
        for i in range(len(self.tokens)):
            tokens = self.tokens[i]
            spaces = self.spaces[i]
            words = [vocab.strings[orth] for orth in tokens[:, orth_col]]
            doc = Doc(vocab, words=words, spaces=spaces)
            doc = doc.from_array(self.attrs, tokens)
            doc.cats = self.cats[i]
            if self.store_user_data:
                user_data = srsly.msgpack_loads(self.user_data[i], use_list=False)
                doc.user_data.update(user_data)
            yield doc

    def merge(self, other):
        """Extend the annotations of this DocBin with the annotations from
        another. Will raise an error if the pre-defined attrs of the two
        DocBins don't match.

        other (DocBin): The DocBin to merge into the current bin.

        DOCS: https://spacy.io/api/docbin#merge
        """
        if self.attrs != other.attrs:
            raise ValueError(Errors.E166.format(current=self.attrs, other=other.attrs))
        self.tokens.extend(other.tokens)
        self.spaces.extend(other.spaces)
        self.strings.update(other.strings)
        self.cats.extend(other.cats)
        if self.store_user_data:
            self.user_data.extend(other.user_data)

    def to_bytes(self):
        """Serialize the DocBin's annotations to a bytestring.

        RETURNS (bytes): The serialized DocBin.

        DOCS: https://spacy.io/api/docbin#to_bytes
        """
        for tokens in self.tokens:
            assert len(tokens.shape) == 2, tokens.shape  # this should never happen
        lengths = [len(tokens) for tokens in self.tokens]
        msg = {
            "attrs": self.attrs,
            "tokens": numpy.vstack(self.tokens).tobytes("C"),
            "spaces": numpy.vstack(self.spaces).tobytes("C"),
            "lengths": numpy.asarray(lengths, dtype="int32").tobytes("C"),
            "strings": list(self.strings),
            "cats": self.cats,
        }
        if self.store_user_data:
            msg["user_data"] = self.user_data
        return zlib.compress(srsly.msgpack_dumps(msg))

    def from_bytes(self, bytes_data):
        """Deserialize the DocBin's annotations from a bytestring.

        bytes_data (bytes): The data to load from.
        RETURNS (DocBin): The loaded DocBin.

        DOCS: https://spacy.io/api/docbin#from_bytes
        """
        msg = srsly.msgpack_loads(zlib.decompress(bytes_data))
        self.attrs = msg["attrs"]
        self.strings = set(msg["strings"])
        lengths = numpy.frombuffer(msg["lengths"], dtype="int32")
        flat_spaces = numpy.frombuffer(msg["spaces"], dtype=bool)
        flat_tokens = numpy.frombuffer(msg["tokens"], dtype="uint64")
        shape = (flat_tokens.size // len(self.attrs), len(self.attrs))
        flat_tokens = flat_tokens.reshape(shape)
        flat_spaces = flat_spaces.reshape((flat_spaces.size, 1))
        self.tokens = NumpyOps().unflatten(flat_tokens, lengths)
        self.spaces = NumpyOps().unflatten(flat_spaces, lengths)
        self.cats = msg["cats"]
        if self.store_user_data and "user_data" in msg:
            self.user_data = list(msg["user_data"])
        for tokens in self.tokens:
            assert len(tokens.shape) == 2, tokens.shape  # this should never happen
        return self


def merge_bins(bins):
    merged = None
    for byte_string in bins:
        if byte_string is not None:
            doc_bin = DocBin(store_user_data=True).from_bytes(byte_string)
            if merged is None:
                merged = doc_bin
            else:
                merged.merge(doc_bin)
    if merged is not None:
        return merged.to_bytes()
    else:
        return b""


def pickle_bin(doc_bin):
    return (unpickle_bin, (doc_bin.to_bytes(),))


def unpickle_bin(byte_string):
    return DocBin().from_bytes(byte_string)


copy_reg.pickle(DocBin, pickle_bin, unpickle_bin)
# Compatibility, as we had named it this previously.
Binder = DocBin

__all__ = ["DocBin"]

# coding: utf8
from __future__ import unicode_literals

import numpy
from spacy.tokens import Doc
from spacy.attrs import DEP, POS, TAG

from ..util import get_doc


def test_issue5048(en_vocab):
    words = ["This", "is", "a", "sentence"]
    pos_s = ["DET", "VERB", "DET", "NOUN"]
    spaces = [" ", " ", " ", ""]
    deps_s = ["dep", "adj", "nn", "atm"]
    tags_s = ["DT", "VBZ", "DT", "NN"]

    strings = en_vocab.strings

    for w in words:
        strings.add(w)
    deps = [strings.add(d) for d in deps_s]
    pos = [strings.add(p) for p in pos_s]
    tags = [strings.add(t) for t in tags_s]

    attrs = [POS, DEP, TAG]
    array = numpy.array(list(zip(pos, deps, tags)), dtype="uint64")

    doc = Doc(en_vocab, words=words, spaces=spaces)
    doc.from_array(attrs, array)
    v1 = [(token.text, token.pos_, token.tag_) for token in doc]

    doc2 = get_doc(en_vocab, words=words, pos=pos_s, deps=deps_s, tags=tags_s)
    v2 = [(token.text, token.pos_, token.tag_) for token in doc2]
    assert v1 == v2

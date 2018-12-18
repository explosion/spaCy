# coding: utf8
from __future__ import unicode_literals

import pytest

from ...attrs import ENT_IOB, ENT_TYPE
from ...tokens import Doc
from ..util import get_doc


@pytest.mark.xfail
def test_issue3012(en_vocab):
    words = ["This", "is", "10", "%", "."]
    tags = ["DT", "VBZ", "CD", "NN", "."]
    pos = ["DET", "VERB", "NUM", "NOUN", "PUNCT"]
    ents = [(2, 4, "PERCENT")]
    doc = get_doc(en_vocab, words=words, tags=tags, pos=pos, ents=ents)

    expected = ("10", "NUM", "CD", "PERCENT")
    assert (doc[2].text, doc[2].pos_, doc[2].tag_, doc[2].ent_type_) == expected

    # now removing '10%' entity
    assert len(doc.ents) == 1
    header = [ENT_IOB, ENT_TYPE]
    ent_array = doc.to_array(header)
    ent = doc.ents[0]
    for idx in range(ent.start, ent.end):
        ent_array[idx, 0] = 0
        ent_array[idx, 1] = 0
    doc.from_array(header, ent_array)
    assert len(doc.ents) == 0

    assert (doc[2].text, doc[2].pos_, doc[2].tag_, doc[2].ent_type_) == expected

    # serializing then deserializing
    doc_bytes = doc.to_bytes()
    doc2 = Doc(en_vocab).from_bytes(doc_bytes)
    assert len(doc2.ents) == 0

    assert (doc[2].text, doc[2].pos_, doc[2].tag_, doc[2].ent_type_) == expected

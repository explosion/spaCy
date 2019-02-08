# coding: utf8
from __future__ import unicode_literals

from ...attrs import ENT_IOB, ENT_TYPE
from ...tokens import Doc
from ..util import get_doc


def test_issue3012(en_vocab):
    """Test that the is_tagged attribute doesn't get overwritten when we from_array
    without tag information."""
    words = ["This", "is", "10", "%", "."]
    tags = ["DT", "VBZ", "CD", "NN", "."]
    pos = ["DET", "VERB", "NUM", "NOUN", "PUNCT"]
    ents = [(2, 4, "PERCENT")]
    doc = get_doc(en_vocab, words=words, tags=tags, pos=pos, ents=ents)
    assert doc.is_tagged

    expected = ("10", "NUM", "CD", "PERCENT")
    assert (doc[2].text, doc[2].pos_, doc[2].tag_, doc[2].ent_type_) == expected

    header = [ENT_IOB, ENT_TYPE]
    ent_array = doc.to_array(header)
    doc.from_array(header, ent_array)

    assert (doc[2].text, doc[2].pos_, doc[2].tag_, doc[2].ent_type_) == expected

    # serializing then deserializing
    doc_bytes = doc.to_bytes()
    doc2 = Doc(en_vocab).from_bytes(doc_bytes)
    assert (doc2[2].text, doc2[2].pos_, doc2[2].tag_, doc2[2].ent_type_) == expected

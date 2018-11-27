# coding: utf-8
from __future__ import unicode_literals

from ..util import get_doc


def test_issue2772(en_vocab):
    """Test that deprojectivization doesn't mess up sentence boundaries."""
    words = "When we write or communicate virtually , we can hide our true feelings .".split()
    # A tree with a non-projective (i.e. crossing) arc
    # The arcs (0, 4) and (2, 9) cross.
    heads = [4, 1, 7, -1, -2, -1, 3, 2, 1, 0, -1, -2, -1]
    deps = ["dep"] * len(heads)
    doc = get_doc(en_vocab, words=words, heads=heads, deps=deps)
    assert doc[1].is_sent_start is None

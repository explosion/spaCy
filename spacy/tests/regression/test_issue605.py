# coding: utf-8
from __future__ import unicode_literals

from ...attrs import ORTH
from ...matcher import Matcher
from ..util import get_doc


def test_issue605(en_vocab):
    def return_false(doc, ent_id, label, start, end):
        return False

    words = ["The", "golf", "club", "is", "broken"]
    pattern = [{ORTH: "golf"}, {ORTH: "club"}]
    label = "Sport_Equipment"
    doc = get_doc(en_vocab, words)
    matcher = Matcher(doc.vocab)
    matcher.add_entity(label, acceptor=return_false)
    matcher.add_pattern(label, pattern)
    match = matcher(doc)
    assert match == []

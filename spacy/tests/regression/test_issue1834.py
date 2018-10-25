from __future__ import unicode_literals
from ...tokens import Doc
from ...vocab import Vocab


def test_issue1834():
    """test if sentence boundaries & parse/tag flags are not lost
    during serialization
    """
    words = "This is a first sentence . And another one".split()
    vocab = Vocab()
    doc = Doc(vocab, words=words)
    vocab = doc.vocab
    doc[6].sent_start = True
    deser_doc = Doc(vocab).from_bytes(doc.to_bytes())
    assert deser_doc[6].sent_start
    assert not deser_doc.is_parsed
    assert not deser_doc.is_tagged
    doc.is_parsed = True
    doc.is_tagged = True
    deser_doc = Doc(vocab).from_bytes(doc.to_bytes())
    assert deser_doc.is_parsed
    assert deser_doc.is_tagged





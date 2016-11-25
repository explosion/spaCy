from ...tokens import Doc
from ...vocab import Vocab

def test_issue599():
    doc = Doc(Vocab())
    doc.is_tagged = True
    doc.is_parsed = True
    bytes_ = doc.to_bytes()
    doc2 = Doc(doc.vocab)
    doc2.from_bytes(bytes_)
    assert doc2.is_parsed

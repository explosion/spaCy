from __future__ import unicode_literals


def test_issue1773(en_tokenizer):
    """Test that spaces don't receive a POS but no TAG. This is the root cause
    of the serialization issue reported in #1773."""
    doc = en_tokenizer('\n')
    if doc[0].pos_ == 'SPACE':
        assert doc[0].tag_ != ""

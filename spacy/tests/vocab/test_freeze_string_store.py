'''Test the possibly temporary workaround of flushing the stringstore of OOV words.'''
import pytest

from ...strings import StringStore


def test_oov():
    strings = StringStore()
    a = strings[u'a']
    b = strings[u'b']

    assert a == 1
    assert b == 2
    strings.set_frozen(True)
    c = strings[u'c']
    assert c >= 4
    c_ = strings[c]
    assert c_ == u'c'
    strings.flush_oov()
    with pytest.raises(IndexError):
        c_ = strings[c]

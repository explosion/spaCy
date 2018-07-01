from __future__ import unicode_literals
import pytest
from ...vocab import Vocab
from ...tokens.doc import Doc


def test_issue1375():
    '''Test that token.nbor() raises IndexError for out-of-bounds access.'''
    doc = Doc(Vocab(), words=['0', '1', '2'])
    with pytest.raises(IndexError):
        assert doc[0].nbor(-1)
    assert doc[1].nbor(-1).text == '0'
    with pytest.raises(IndexError):
        assert doc[2].nbor(1)
    assert doc[1].nbor(1).text == '2'
 

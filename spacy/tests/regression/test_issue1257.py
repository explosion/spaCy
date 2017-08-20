'''Test tokens compare correctly'''
from __future__ import unicode_literals

from ..util import get_doc
from ...vocab import Vocab


def test_issue1257():
    doc1 = get_doc(Vocab(), ['a', 'b', 'c'])
    doc2 = get_doc(Vocab(), ['a', 'c', 'e'])
    assert doc1[0] != doc2[0]
    assert not doc1[0] == doc2[0]

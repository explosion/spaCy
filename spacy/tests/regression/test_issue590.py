# coding: utf-8
from __future__ import unicode_literals

from ...matcher import Matcher
from ..util import get_doc


def test_issue590(en_vocab):
    """Test overlapping matches"""
    doc = get_doc(en_vocab, ['n', '=', '1', ';', 'a', ':', '5', '%'])
    matcher = Matcher(en_vocab)
    matcher.add('ab', None, [{'IS_ALPHA': True}, {'ORTH': ':'}, {'LIKE_NUM': True}, {'ORTH': '%'}])
    matcher.add('ab', None, [{'IS_ALPHA': True}, {'ORTH': '='}, {'LIKE_NUM': True}])
    matches = matcher(doc)
    assert len(matches) == 2

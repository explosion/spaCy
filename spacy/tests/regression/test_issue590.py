# coding: utf-8
from __future__ import unicode_literals

from ...attrs import ORTH, IS_ALPHA, LIKE_NUM
from ...matcher import Matcher
from ..util import get_doc


def test_issue590(en_vocab):
    """Test overlapping matches"""
    doc = get_doc(en_vocab, ['n', '=', '1', ';', 'a', ':', '5', '%'])

    matcher = Matcher(en_vocab)
    matcher.add_entity("ab", acceptor=None, on_match=None)
    matcher.add_pattern('ab', [{IS_ALPHA: True}, {ORTH: ':'},
                               {LIKE_NUM: True}, {ORTH: '%'}],
                               label='a')
    matcher.add_pattern('ab', [{IS_ALPHA: True}, {ORTH: '='},
                               {LIKE_NUM: True}],
                               label='b')
    matches = matcher(doc)
    assert len(matches) == 2

from __future__ import unicode_literals
from ...attrs import *
from ...matcher import Matcher
from ...tokens import Doc
from ...en import English

def test_overlapping_matches():
    vocab = English.Defaults.create_vocab()
    doc = Doc(vocab, words=['n', '=', '1', ';', 'a', ':', '5', '%'])

    matcher = Matcher(vocab)
    matcher.add_entity(
        "ab",
        acceptor=None,
        on_match=None
    )
    matcher.add_pattern(
        'ab',
        [
            {IS_ALPHA: True},
            {ORTH: ':'},
            {LIKE_NUM: True},
            {ORTH: '%'}
        ], label='a')
    matcher.add_pattern(
        'ab',
        [
            {IS_ALPHA: True},
            {ORTH: '='},
            {LIKE_NUM: True},
        ], label='b')
 
    matches = matcher(doc)
    assert len(matches) == 2

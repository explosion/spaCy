from __future__ import unicode_literals

from ...vocab import Vocab
from ...lang.lex_attrs import LEX_ATTRS
from ...tokens import Doc
from ...matcher import Matcher


def test_issue1434():
    '''Test matches occur when optional element at end of short doc'''
    vocab = Vocab(lex_attr_getters=LEX_ATTRS)
    hello_world = Doc(vocab, words=['Hello', 'World'])
    hello = Doc(vocab, words=['Hello'])

    matcher = Matcher(vocab)
    matcher.add('MyMatcher', None,
        [ {'ORTH': 'Hello' }, {'IS_ALPHA': True, 'OP': '?'} ])

    matches = matcher(hello_world)
    assert matches
    matches = matcher(hello)
    assert matches

from __future__ import unicode_literals

import pytest

from spacy.attrs import *




def test_lexeme_lt(en_vocab):
    '''More frequent is l.t. less frequent'''
    noun = en_vocab['NOUN']

    opera = en_vocab['opera']

    assert noun < opera
    assert opera > noun


def test_lexeme_hash(en_vocab):
    '''Test that lexemes are hashable.'''
    phantom = en_vocab['phantom']

    opera = en_vocab['opera']

    lexes = {phantom: phantom, opera: opera}
    assert lexes[phantom].orth_ == 'phantom'
    assert lexes[opera].orth_ == 'opera'

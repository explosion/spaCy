from __future__ import unicode_literals

import pytest

from spacy.en import *
from spacy.lexeme import *


def test_is_alpha():
    the = EN.lexicon.lookup('the')
    assert the.check_orth_flag(LexOrth_alpha)
    year = EN.lexicon.lookup('1999')
    assert not year.check_orth_flag(LexOrth_alpha)
    mixed = EN.lexicon.lookup('hello1')
    assert not mixed.check_orth_flag(LexOrth_alpha)


def test_is_digit():
    the = EN.lexicon.lookup('the')
    assert not the.check_orth_flag(LexOrth_digit)
    year = EN.lexicon.lookup('1999')
    assert year.check_orth_flag(LexOrth_digit)
    mixed = EN.lexicon.lookup('hello1')
    assert not mixed.check_orth_flag(LexOrth_digit)



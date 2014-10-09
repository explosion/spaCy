from __future__ import unicode_literals

import pytest

from spacy.en import *
from spacy.lexeme import *


def test_is_alpha():
    the = EN.lookup('the')
    assert the.check_orth_flag(LexOrth_alpha)
    year = EN.lookup('1999')
    assert not year.check_orth_flag(LexOrth_alpha)
    mixed = EN.lookup('hello1')
    assert not mixed.check_orth_flag(LexOrth_alpha)


def test_is_digit():
    the = EN.lookup('the')
    assert not the.check_orth_flag(LexOrth_digit)
    year = EN.lookup('1999')
    assert year.check_orth_flag(LexOrth_digit)
    mixed = EN.lookup('hello1')
    assert not mixed.check_orth_flag(LexOrth_digit)



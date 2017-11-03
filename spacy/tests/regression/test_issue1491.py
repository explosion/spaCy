# coding: utf8
from __future__ import unicode_literals

import pytest
import regex as re

from ...lang.en import English
from ...tokenizer import Tokenizer


@pytest.mark.xfail
def test_issue1491():
    """Test possible off-by-one error in tokenizer prefix/suffix/infix rules."""
    prefix_re = re.compile(r'''[\[\("']''')
    suffix_re = re.compile(r'''[\]\)"']''')
    infix_re = re.compile(r'''[-~]''')

    def my_tokenizer(nlp):
        return Tokenizer(nlp.vocab, {},
                         prefix_search=prefix_re.search,
                         suffix_search=suffix_re.search,
                         infix_finditer=infix_re.finditer)

    nlp = English()
    nlp.tokenizer = my_tokenizer(nlp)
    doc = nlp("single quote 'goodbye end.")
    tokens = [token.text for token in doc]
    assert tokens == ['single', 'quote', "'", 'goodbye', 'end', '.']

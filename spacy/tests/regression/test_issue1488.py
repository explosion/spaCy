# coding: utf8
from __future__ import unicode_literals

import regex as re
from ...lang.en import English
from ...tokenizer import Tokenizer


def test_issue1488():
    prefix_re = re.compile(r'''[\[\("']''')
    suffix_re = re.compile(r'''[\]\)"']''')
    infix_re = re.compile(r'''[-~\.]''')
    simple_url_re = re.compile(r'''^https?://''')

    def my_tokenizer(nlp):
        return Tokenizer(nlp.vocab, {},
                         prefix_search=prefix_re.search,
                         suffix_search=suffix_re.search,
                         infix_finditer=infix_re.finditer,
                         token_match=simple_url_re.match)

    nlp = English()
    nlp.tokenizer = my_tokenizer(nlp)
    doc = nlp("This is a test.")
    for token in doc:
        assert token.text

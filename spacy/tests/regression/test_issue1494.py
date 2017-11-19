# coding: utf8
from __future__ import unicode_literals

import pytest
import re

from ...lang.en import English
from ...tokenizer import Tokenizer


def test_issue1494():    
    infix_re = re.compile(r'''[^a-z]''')
    text_to_tokenize = 'token 123test'
    expected_tokens = ['token', '1', '2', '3', 'test']
    
    def my_tokenizer(nlp):
        return Tokenizer(nlp.vocab,
                     {},
                     infix_finditer=infix_re.finditer
    )

    nlp = English()

    nlp.tokenizer = my_tokenizer(nlp)
    tokenized_words = [token.text for token in nlp(text_to_tokenize)]
    print(tokenized_words)
    assert tokenized_words == expected_tokens    

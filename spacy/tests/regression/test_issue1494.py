# coding: utf8
from __future__ import unicode_literals

import pytest
import re

from ...lang.en import English
from ...tokenizer import Tokenizer


def test_issue1494():    
    infix_re = re.compile(r'''[^a-z]''')
    text_to_tokenize1 = 'token 123test'
    expected_tokens1 = ['token', '1', '2', '3', 'test']

    text_to_tokenize2 = 'token 1test'
    expected_tokens2 = ['token', '1test']

    text_to_tokenize3 = 'hello...test'
    expected_tokens3 = ['hello', '.', '.', '.', 'test']
    
    def my_tokenizer(nlp):
        return Tokenizer(nlp.vocab,
                     {},
                     infix_finditer=infix_re.finditer
    )

    nlp = English()

    nlp.tokenizer = my_tokenizer(nlp)

    tokenized_words1 = [token.text for token in nlp(text_to_tokenize1)]
    assert tokenized_words1 == expected_tokens1

    tokenized_words2 = [token.text for token in nlp(text_to_tokenize2)]
    assert tokenized_words2 == expected_tokens2

    tokenized_words3 = [token.text for token in nlp(text_to_tokenize3)]
    assert tokenized_words3 == expected_tokens3

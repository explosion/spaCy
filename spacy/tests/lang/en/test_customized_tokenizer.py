# coding: utf-8
from __future__ import unicode_literals

import pytest

from ....lang.en import English
from ....tokenizer import Tokenizer
from .... import util


@pytest.fixture
def custom_en_tokenizer(en_vocab):
    prefix_re = util.compile_prefix_regex(English.Defaults.prefixes)
    suffix_re = util.compile_suffix_regex(English.Defaults.suffixes)
    custom_infixes = ['\.\.\.+',
                      '(?<=[0-9])-(?=[0-9])',
                      # '(?<=[0-9]+),(?=[0-9]+)',
                      '[0-9]+(,[0-9]+)+',
                      '[\[\]!&:,()\*—–\/-]']

    infix_re = util.compile_infix_regex(custom_infixes)
    return Tokenizer(en_vocab,
                     English.Defaults.tokenizer_exceptions,
                     prefix_re.search,
                     suffix_re.search,
                     infix_re.finditer,
                     token_match=None)


def test_customized_tokenizer_handles_infixes(custom_en_tokenizer):
    sentence = "The 8 and 10-county definitions are not used for the greater Southern California Megaregion."
    context = [word.text for word in custom_en_tokenizer(sentence)]
    assert context == ['The', '8', 'and', '10', '-', 'county', 'definitions',
                       'are', 'not', 'used', 'for', 'the', 'greater',
                       'Southern', 'California', 'Megaregion', '.']

    # the trailing '-' may cause Assertion Error
    sentence = "The 8- and 10-county definitions are not used for the greater Southern California Megaregion."
    context = [word.text for word in custom_en_tokenizer(sentence)]
    assert context == ['The', '8', '-', 'and', '10', '-', 'county',
                       'definitions', 'are', 'not', 'used', 'for', 'the',
                       'greater', 'Southern', 'California', 'Megaregion', '.']

# coding: utf-8
from __future__ import unicode_literals

from ... import load
from ...tokenizer import Tokenizer
from ... import util

import pytest


def test_customized_tokenizer_handles_infixes():
    def custom_tokenizer(nlp_model):
        prefix_re = util.compile_prefix_regex(nlp_model.Defaults.prefixes)
        suffix_re = util.compile_suffix_regex(nlp_model.Defaults.suffixes)
        custom_infixes = ['\.\.\.+',
                          '(?<=[0-9])-(?=[0-9])',
                          # '(?<=[0-9]+),(?=[0-9]+)',
                          '[0-9]+(,[0-9]+)+',
                          u'[\[\]!&:,()\*—–\/-]']

        infix_re = util.compile_infix_regex(custom_infixes)

        # infix_re = re.compile(ur'[\[\]!&:,()]')

        tokenizer = Tokenizer(nlp_model.vocab,
                              nlp_model.Defaults.tokenizer_exceptions,
                              prefix_re.search,
                              suffix_re.search,
                              infix_re.finditer,
                              token_match=None)
        return lambda text: tokenizer(text)

    nlp = load('en', create_make_doc=custom_tokenizer)

    sentence = "The 8 and 10-county definitions are not used for the greater Southern California Megaregion."
    context = [word.text for word in nlp(sentence)]
    assert context == [u'The', u'8', u'and', u'10', u'-', u'county', u'definitions', u'are', u'not', u'used',
                       u'for',
                       u'the', u'greater', u'Southern', u'California', u'Megaregion', u'.']

    # the trailing '-' may cause Assertion Error
    sentence = "The 8- and 10-county definitions are not used for the greater Southern California Megaregion."
    context = [word.text for word in nlp(sentence)]
    assert context == [u'The', u'8', u'-', u'and', u'10', u'-', u'county', u'definitions', u'are', u'not', u'used',
                       u'for',
                       u'the', u'greater', u'Southern', u'California', u'Megaregion', u'.']

# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.lang.en import English
from spacy.tokenizer import Tokenizer
from spacy.util import compile_prefix_regex, compile_suffix_regex
from spacy.util import compile_infix_regex


@pytest.fixture
def custom_en_tokenizer(en_vocab):
    prefix_re = compile_prefix_regex(English.Defaults.prefixes)
    suffix_re = compile_suffix_regex(English.Defaults.suffixes)
    custom_infixes = [
        r"\.\.\.+",
        r"(?<=[0-9])-(?=[0-9])",
        r"[0-9]+(,[0-9]+)+",
        r"[\[\]!&:,()\*—–\/-]",
    ]
    infix_re = compile_infix_regex(custom_infixes)
    return Tokenizer(
        en_vocab,
        English.Defaults.tokenizer_exceptions,
        prefix_re.search,
        suffix_re.search,
        infix_re.finditer,
        token_match=None,
    )


def test_en_customized_tokenizer_handles_infixes(custom_en_tokenizer):
    sentence = "The 8 and 10-county definitions are not used for the greater Southern California Megaregion."
    context = [word.text for word in custom_en_tokenizer(sentence)]
    assert context == [
        "The",
        "8",
        "and",
        "10",
        "-",
        "county",
        "definitions",
        "are",
        "not",
        "used",
        "for",
        "the",
        "greater",
        "Southern",
        "California",
        "Megaregion",
        ".",
    ]
    # the trailing '-' may cause Assertion Error
    sentence = "The 8- and 10-county definitions are not used for the greater Southern California Megaregion."
    context = [word.text for word in custom_en_tokenizer(sentence)]
    assert context == [
        "The",
        "8",
        "-",
        "and",
        "10",
        "-",
        "county",
        "definitions",
        "are",
        "not",
        "used",
        "for",
        "the",
        "greater",
        "Southern",
        "California",
        "Megaregion",
        ".",
    ]

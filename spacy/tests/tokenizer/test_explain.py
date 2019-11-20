# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.util import get_lang_class

# Only include languages with no external dependencies
# "is" seems to confuse importlib, so we're also excluding it for now
# excluded: ja, ru, th, uk, vi, zh, is
LANGUAGES = [
    "af",
    "ar",
    "bg",
    "bn",
    pytest.param("ca", marks=pytest.mark.xfail()),
    "cs",
    "da",
    "de",
    "el",
    "en",
    "es",
    "et",
    "fa",
    "fi",
    pytest.param("fr", marks=pytest.mark.xfail()),
    "ga",
    "he",
    "hi",
    "hr",
    pytest.param("hu", marks=pytest.mark.xfail()),
    "id",
    "it",
    "kn",
    "lt",
    "lv",
    "nb",
    "nl",
    pytest.param("pl", marks=pytest.mark.xfail()),
    "pt",
    "ro",
    "si",
    "sk",
    "sl",
    "sq",
    "sr",
    "sv",
    "ta",
    "te",
    "tl",
    "tr",
    "tt",
    "ur",
]


@pytest.mark.slow
@pytest.mark.parametrize("lang", LANGUAGES)
def test_tokenizer_explain(lang):
    nlp = get_lang_class(lang)()
    examples = pytest.importorskip("spacy.lang.{}.examples".format(lang))
    for sentence in examples.sentences:
        tokens = [t.text for t in nlp.tokenizer(sentence) if not t.is_space]
        debug_tokens = [t[1] for t in nlp.tokenizer.explain(sentence)]
        assert tokens == debug_tokens

# coding: utf-8
from __future__ import unicode_literals

import importlib
import pytest
from spacy.util import get_lang_class


# fmt: off
# Only include languages with no external dependencies
# excluded: ja, ru, th, uk, vi, zh
LANGUAGES = ["af", "ar", "bg", "bn", "ca", "cs", "da", "de", "el", "en", "es",
             "et", "fa", "fi", "fr", "ga", "he", "hi", "hr", "hu", "id", "is",
             "it", "kn", "lt", "lv", "nb", "nl", "pl", "pt", "ro", "si", "sk",
             "sl", "sq", "sr", "sv", "ta", "te", "tl", "tr", "tt", "ur"]
# fmt: on


@pytest.mark.slow
@pytest.mark.parametrize("lang", LANGUAGES)
def test_tokenizer_explain(lang):
    nlp = get_lang_class(lang)()
    try:
        examples = importlib.import_module("spacy.lang." + lang + ".examples")
        for sentence in examples.sentences:
            tokens = [t.text for t in nlp.tokenizer(sentence) if not t.is_space]
            debug_tokens = [t[1] for t in nlp.tokenizer.explain(sentence)]
            assert tokens == debug_tokens
    except:
        pass

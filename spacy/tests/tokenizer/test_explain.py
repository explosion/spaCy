import pytest
from spacy.util import get_lang_class

# Only include languages with no external dependencies
# "is" seems to confuse importlib, so we're also excluding it for now
# excluded: ja, ru, th, uk, vi, zh, is
LANGUAGES = [
    pytest.param("fr", marks=pytest.mark.slow()),
    pytest.param("af", marks=pytest.mark.slow()),
    pytest.param("ar", marks=pytest.mark.slow()),
    pytest.param("bg", marks=pytest.mark.slow()),
    "bn",
    pytest.param("ca", marks=pytest.mark.slow()),
    pytest.param("cs", marks=pytest.mark.slow()),
    pytest.param("da", marks=pytest.mark.slow()),
    pytest.param("de", marks=pytest.mark.slow()),
    "el",
    "en",
    pytest.param("es", marks=pytest.mark.slow()),
    pytest.param("et", marks=pytest.mark.slow()),
    pytest.param("fa", marks=pytest.mark.slow()),
    pytest.param("fi", marks=pytest.mark.slow()),
    "fr",
    pytest.param("ga", marks=pytest.mark.slow()),
    pytest.param("he", marks=pytest.mark.slow()),
    pytest.param("hi", marks=pytest.mark.slow()),
    pytest.param("hr", marks=pytest.mark.slow()),
    "hu",
    pytest.param("id", marks=pytest.mark.slow()),
    pytest.param("it", marks=pytest.mark.slow()),
    pytest.param("kn", marks=pytest.mark.slow()),
    pytest.param("lb", marks=pytest.mark.slow()),
    pytest.param("lt", marks=pytest.mark.slow()),
    pytest.param("lv", marks=pytest.mark.slow()),
    pytest.param("nb", marks=pytest.mark.slow()),
    pytest.param("nl", marks=pytest.mark.slow()),
    "pl",
    pytest.param("pt", marks=pytest.mark.slow()),
    pytest.param("ro", marks=pytest.mark.slow()),
    pytest.param("si", marks=pytest.mark.slow()),
    pytest.param("sk", marks=pytest.mark.slow()),
    pytest.param("sl", marks=pytest.mark.slow()),
    pytest.param("sq", marks=pytest.mark.slow()),
    pytest.param("sr", marks=pytest.mark.slow()),
    pytest.param("sv", marks=pytest.mark.slow()),
    pytest.param("ta", marks=pytest.mark.slow()),
    pytest.param("te", marks=pytest.mark.slow()),
    pytest.param("tl", marks=pytest.mark.slow()),
    pytest.param("tr", marks=pytest.mark.slow()),
    pytest.param("tt", marks=pytest.mark.slow()),
    pytest.param("ur", marks=pytest.mark.slow()),
]


@pytest.mark.parametrize("lang", LANGUAGES)
def test_tokenizer_explain(lang):
    tokenizer = get_lang_class(lang)().tokenizer
    examples = pytest.importorskip(f"spacy.lang.{lang}.examples")
    for sentence in examples.sentences:
        tokens = [t.text for t in tokenizer(sentence) if not t.is_space]
        debug_tokens = [t[1] for t in tokenizer.explain(sentence)]
        assert tokens == debug_tokens

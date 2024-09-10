import pytest

from spacy.util import get_lang_class

# fmt: off
# Only include languages with no external dependencies
# excluded: ja, ko, th, vi, zh
LANGUAGES = ["af", "am", "ar", "az", "bg", "bn", "ca", "cs", "da", "de", "el",
             "en", "es", "et", "eu", "fa", "fi", "fr", "ga", "gu", "he", "hi",
             "hr", "hu", "hy", "id", "is", "it", "kn", "ky", "lb", "lt", "lv",
             "mk", "ml", "mr", "nb", "ne", "nl", "pl", "pt", "ro", "ru", "sa",
             "si", "sk", "sl", "sq", "sr", "sv", "ta", "te", "ti", "tl", "tn",
             "tr", "tt", "uk", "ur", "xx", "yo", "kmr"]
# fmt: on


@pytest.mark.parametrize("lang", LANGUAGES)
def test_lang_initialize(lang, capfd):
    """Test that languages can be initialized."""
    nlp = get_lang_class(lang)()
    # Check for stray print statements (see #3342)
    doc = nlp("test")  # noqa: F841
    captured = capfd.readouterr()
    assert not captured.out

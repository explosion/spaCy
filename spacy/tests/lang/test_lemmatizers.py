import pytest
from spacy.util import get_lang_class


# fmt: off
# Only include languages with no external dependencies
# excluded: ru, uk
LANGUAGES = ["el", "en", "fr", "nl", "pl"]
# fmt: on


@pytest.mark.parametrize("lang", LANGUAGES)
def test_lang_initialize(lang, capfd):
    """Test that languages can be initialized."""
    nlp = get_lang_class(lang)()
    nlp.add_pipe("lemmatizer")
    # Check for stray print statements (see #3342)
    doc = nlp("test")  # noqa: F841
    captured = capfd.readouterr()
    assert not captured.out

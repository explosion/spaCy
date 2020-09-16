import pytest
from spacy import registry
from spacy.lookups import Lookups
from spacy.util import get_lang_class


# fmt: off
# Only include languages with no external dependencies
# excluded: ru, uk
# excluded for custom tables: pl
LANGUAGES = ["bn", "el", "en", "fa", "fr", "nb", "nl", "sv"]
# fmt: on


@pytest.mark.parametrize("lang", LANGUAGES)
def test_lemmatizer_initialize(lang, capfd):
    @registry.misc("lemmatizer_init_lookups")
    def lemmatizer_init_lookups():
        lookups = Lookups()
        lookups.add_table("lemma_lookup", {"cope": "cope"})
        lookups.add_table("lemma_index", {"verb": ("cope", "cop")})
        lookups.add_table("lemma_exc", {"verb": {"coping": ("cope",)}})
        lookups.add_table("lemma_rules", {"verb": [["ing", ""]]})
        return lookups

    """Test that languages can be initialized."""
    nlp = get_lang_class(lang)()
    nlp.add_pipe("lemmatizer", config={"lookups": {"@misc": "lemmatizer_init_lookups"}})
    # Check for stray print statements (see #3342)
    doc = nlp("test")  # noqa: F841
    captured = capfd.readouterr()
    assert not captured.out

import pytest
from spacy import registry
from spacy.lookups import Lookups
from spacy.util import get_lang_class


# fmt: off
# Only include languages with no external dependencies
# excluded: ru, uk
# excluded for custom tables: pl
LANGUAGES = ["el", "en", "fr", "nl"]
# fmt: on

@registry.assets("cope_lookups")
def cope_lookups():
    lookups = Lookups()
    lookups.add_table("lemma_lookup", {"cope": "cope"})
    lookups.add_table("lemma_index", {"verb": ("cope", "cop")})
    lookups.add_table("lemma_exc", {"verb": {"coping": ("cope",)}})
    lookups.add_table("lemma_rules", {"verb": [["ing", ""]]})
    return lookups


@pytest.mark.parametrize("lang", LANGUAGES)
def test_lang_initialize(lang, capfd):
    """Test that languages can be initialized."""
    nlp = get_lang_class(lang)()
    nlp.add_pipe("lemmatizer", config={"lookups": {"@assets": "cope_lookups"}})
    # Check for stray print statements (see #3342)
    doc = nlp("test")  # noqa: F841
    captured = capfd.readouterr()
    assert not captured.out

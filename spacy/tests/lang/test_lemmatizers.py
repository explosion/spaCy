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
        lookups.add_table("lemma_lookup", {"cope": "cope", "x": "y"})
        lookups.add_table("lemma_index", {"verb": ("cope", "cop")})
        lookups.add_table("lemma_exc", {"verb": {"coping": ("cope",)}})
        lookups.add_table("lemma_rules", {"verb": [["ing", ""]]})
        return lookups

    # Test that languages can be initialized
    nlp = get_lang_class(lang)()
    lemmatizer = nlp.add_pipe("lemmatizer", config={"mode": "lookup"})
    assert not lemmatizer.lookups.tables
    nlp.config["initialize"]["components"]["lemmatizer"] = {
        "lookups": {"@misc": "lemmatizer_init_lookups"}
    }
    with pytest.raises(ValueError):
        nlp("x")
    nlp.initialize()
    assert lemmatizer.lookups.tables
    doc = nlp("x")
    # Check for stray print statements (see #3342)
    captured = capfd.readouterr()
    assert not captured.out
    assert doc[0].lemma_ == "y"

    # Test initialization by calling .initialize() directly
    nlp = get_lang_class(lang)()
    lemmatizer = nlp.add_pipe("lemmatizer", config={"mode": "lookup"})
    lemmatizer.initialize(lookups=lemmatizer_init_lookups())
    assert nlp("x")[0].lemma_ == "y"

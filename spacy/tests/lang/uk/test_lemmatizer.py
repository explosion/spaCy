import pytest
from spacy.tokens import Doc


pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")


def test_uk_lemmatizer(uk_lemmatizer):
    """Check that the default uk lemmatizer runs."""
    doc = Doc(uk_lemmatizer.vocab, words=["a", "b", "c"])
    assert uk_lemmatizer.mode == "pymorphy3"
    uk_lemmatizer(doc)
    assert [token.lemma for token in doc]


@pytest.mark.parametrize(
    "word,lemma",
    (
        ("якийсь", "якийсь"),
        ("розповідають", "розповідати"),
        ("розповіси", "розповісти"),
    ),
)
def test_uk_lookup_lemmatizer(uk_lookup_lemmatizer, word, lemma):
    assert uk_lookup_lemmatizer.mode == "pymorphy3_lookup"
    doc = Doc(uk_lookup_lemmatizer.vocab, words=[word])
    assert uk_lookup_lemmatizer(doc)[0].lemma_ == lemma

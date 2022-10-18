import pytest
from spacy.tokens import Doc


pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")


def test_uk_lemmatizer(uk_lemmatizer):
    """Check that the default uk lemmatizer runs."""
    doc = Doc(uk_lemmatizer.vocab, words=["a", "b", "c"])
    uk_lemmatizer(doc)
    assert [token.lemma for token in doc]


def test_uk_lookup_lemmatizer(uk_lookup_lemmatizer):
    """Check that the lookup uk lemmatizer runs."""
    doc = Doc(uk_lookup_lemmatizer.vocab, words=["a", "b", "c"])
    uk_lookup_lemmatizer(doc)
    assert [token.lemma for token in doc]

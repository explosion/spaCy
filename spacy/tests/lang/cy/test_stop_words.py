import pytest

from spacy.lang.cy.stop_words import STOP_WORDS

# The eighteen most frequent words by document frequency in the Unit's corpus.
CORPUS_FREQUENT = [
    "yn", "y", "a", "o", "i", "ar", "ac", "yr", "mae", "ei", "gan", "mewn",
    "am", "wedi", "eu", "un", "fel", "hyn",
]  # fmt: skip


@pytest.mark.parametrize("word", CORPUS_FREQUENT)
def test_cy_stop_words_cover_frequent_words(word):
    assert word in STOP_WORDS


@pytest.mark.parametrize("word", ["cath", "Cymru", "cerdded"])
def test_cy_stop_words_exclude_content_words(word):
    assert word not in STOP_WORDS


@pytest.mark.parametrize("word", ["'r", "'n", "’r", "’n"])
def test_cy_stop_words_cover_apostrophe_variants(word):
    assert word in STOP_WORDS


@pytest.mark.parametrize(
    "text", ["Mae'r gath yn cysgu ar y mat", "Mae’r gath yn cysgu ar y mat"]
)
def test_cy_tokenizer_marks_stop_words(cy_tokenizer, text):
    tokens = cy_tokenizer(text)
    assert [t.is_stop for t in tokens] == [
        True,
        True,
        False,
        True,
        False,
        True,
        True,
        False,
    ]

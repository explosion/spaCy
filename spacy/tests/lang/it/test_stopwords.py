import pytest


@pytest.mark.parametrize(
    "word", ["un", "lo", "dell", "dall", "si", "ti", "mi", "quest", "quel", "quello"]
)
def test_stopwords_basic(it_tokenizer, word):
    tok = it_tokenizer(word)[0]
    assert tok.is_stop


@pytest.mark.parametrize(
    "word", ["quest'uomo", "l'ho", "un'amica", "dell'olio", "s'arrende", "m'ascolti"]
)
def test_stopwords_elided(it_tokenizer, word):
    tok = it_tokenizer(word)[0]
    assert tok.is_stop

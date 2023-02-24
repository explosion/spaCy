import pytest


@pytest.mark.parametrize(
    "word,lemma",
    [
        ("새로운", "새롭+ᆫ"),
        ("빨간", "빨갛+ᆫ"),
        ("클수록", "크+ᆯ수록"),
        ("뭡니까", "뭣+이+ᄇ니까"),
        ("됐다", "되+었"),
    ],
)
def test_ko_lemmatizer_assigns(ko_tokenizer, word, lemma):
    test_lemma = ko_tokenizer(word)[0].lemma_
    assert test_lemma == lemma

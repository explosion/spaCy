import pytest


@pytest.mark.parametrize(
    "word,lemma", [("새로운", "새롭"), ("빨간", "빨갛"), ("클수록", "크"), ("뭡니까", "뭣"), ("됐다", "되")]
)
def test_ko_lemmatizer_assigns(ko_tokenizer, word, lemma):
    test_lemma = ko_tokenizer(word)[0].lemma_
    assert test_lemma == lemma

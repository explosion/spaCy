import pytest

from spacy.lang.en import English


@pytest.mark.parametrize(
    "word",
    [
        "don't",
        "don’t",
        "I'd",
        "I’d",
    ],
)
def test_issue3521(fr_tokenizer, word):
    nlp = English()

    tok = nlp(word)[1]
    assert tok.is_stop


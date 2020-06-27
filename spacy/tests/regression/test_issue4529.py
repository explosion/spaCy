import pytest

from spacy.gold import Example


@pytest.mark.parametrize(
    "text,words", [("A'B C", ["A", "'", "B", "C"]), ("A-B", ["A-B"])]
)
def test_gold_misaligned(en_tokenizer, text, words):
    doc = en_tokenizer(text)
    Example.from_dict(doc, {"words": words})

import pytest
from spacy.compat import is_python2
from spacy.gold import GoldParse


@pytest.mark.parametrize(
    "text,words", [("A'B C", ["A", "'", "B", "C"]), ("A-B", ["A-B"])]
)
@pytest.mark.skipif(is_python2, reason="I don't want to spend time on python2 support")
def test_gold_misaligned(en_tokenizer, text, words):
    doc = en_tokenizer(text)
    GoldParse(doc, words=words)

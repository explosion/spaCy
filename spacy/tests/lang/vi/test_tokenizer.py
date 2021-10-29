import pytest

from ...tokenizer.test_naughty_strings import NAUGHTY_STRINGS
from spacy.lang.vi import Vietnamese


# fmt: off
TOKENIZER_TESTS = [
    ("Đây là một văn  bản bằng tiếng Việt Sau đó, đây là một văn bản khác bằng ngôn ngữ này", ['Đây', 'là', 'một', 'văn  bản', 'bằng', 'tiếng', 'Việt', 'Sau', 'đó', ',', 'đây', 'là', 'một', 'văn bản', 'khác', 'bằng', 'ngôn ngữ', 'này']),
]
# fmt: on


@pytest.mark.parametrize("text,expected_tokens", TOKENIZER_TESTS)
def test_vi_tokenizer(vi_tokenizer, text, expected_tokens):
    tokens = [token.text for token in vi_tokenizer(text)]
    assert tokens == expected_tokens


def test_vi_tokenizer_extra_spaces(vi_tokenizer):
    # note: three spaces after "I"
    tokens = vi_tokenizer("I   like cheese.")
    assert tokens[1].orth_ == "  "


@pytest.mark.parametrize("text", NAUGHTY_STRINGS)
def test_vi_tokenizer_naughty_strings(vi_tokenizer, text):
    tokens = vi_tokenizer(text)
    assert tokens.text_with_ws == text


def test_vi_tokenizer_emptyish_texts(vi_tokenizer):
    doc = vi_tokenizer("")
    assert len(doc) == 0
    doc = vi_tokenizer(" ")
    assert len(doc) == 1
    doc = vi_tokenizer("\n\n\n \t\t \n\n\n")
    assert len(doc) == 1


def test_vi_tokenizer_no_pyvi():
    """Test for whitespace tokenization without pyvi"""
    nlp = Vietnamese.from_config({"nlp": {"tokenizer": {"use_pyvi": False}}})
    text = "Đây là một văn  bản bằng tiếng Việt Sau đó, đây là một văn bản khác bằng ngôn ngữ này"
    doc = nlp(text)
    assert [t.text for t in doc if not t.is_space] == text.split()
    assert doc[4].text == " "

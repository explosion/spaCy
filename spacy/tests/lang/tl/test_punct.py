import pytest

from spacy.lang.punctuation import TOKENIZER_PREFIXES
from spacy.util import compile_prefix_regex

PUNCT_OPEN = ["(", "[", "{", "*"]
PUNCT_CLOSE = [")", "]", "}", "*"]
PUNCT_PAIRED = [("(", ")"), ("[", "]"), ("{", "}"), ("*", "*")]


@pytest.mark.parametrize("text", ["(", "((", "<"])
def test_tl_tokenizer_handles_only_punct(tl_tokenizer, text):
    tokens = tl_tokenizer(text)
    assert len(tokens) == len(text)


@pytest.mark.parametrize("punct", PUNCT_OPEN)
@pytest.mark.parametrize("text", ["Mabuhay"])
def test_tl_tokenizer_split_open_punct(tl_tokenizer, punct, text):
    tokens = tl_tokenizer(punct + text)
    assert len(tokens) == 2
    assert tokens[0].text == punct
    assert tokens[1].text == text


@pytest.mark.parametrize("punct", PUNCT_CLOSE)
@pytest.mark.parametrize("text", ["Mabuhay"])
def test_tl_tokenizer_splits_close_punct(tl_tokenizer, punct, text):
    tokens = tl_tokenizer(text + punct)
    assert len(tokens) == 2
    assert tokens[0].text == text
    assert tokens[1].text == punct


@pytest.mark.parametrize("punct", PUNCT_OPEN)
@pytest.mark.parametrize("punct_add", ["`"])
@pytest.mark.parametrize("text", ["Mabuhay"])
def test_tl_tokenizer_splits_two_diff_open_punct(tl_tokenizer, punct, punct_add, text):
    tokens = tl_tokenizer(punct + punct_add + text)
    assert len(tokens) == 3
    assert tokens[0].text == punct
    assert tokens[1].text == punct_add
    assert tokens[2].text == text


@pytest.mark.parametrize("punct", PUNCT_CLOSE)
@pytest.mark.parametrize("punct_add", ["`"])
@pytest.mark.parametrize("text", ["Mabuhay"])
def test_tl_tokenizer_splits_two_diff_close_punct(tl_tokenizer, punct, punct_add, text):
    tokens = tl_tokenizer(text + punct + punct_add)
    assert len(tokens) == 3
    assert tokens[0].text == text
    assert tokens[1].text == punct
    assert tokens[2].text == punct_add


@pytest.mark.parametrize("punct", PUNCT_OPEN)
@pytest.mark.parametrize("text", ["Mabuhay"])
def test_tl_tokenizer_splits_same_open_punct(tl_tokenizer, punct, text):
    tokens = tl_tokenizer(punct + punct + punct + text)
    assert len(tokens) == 4
    assert tokens[0].text == punct
    assert tokens[3].text == text


@pytest.mark.parametrize("punct", PUNCT_CLOSE)
@pytest.mark.parametrize("text", ["Mabuhay"])
def test_tl_tokenizer_splits_same_close_punct(tl_tokenizer, punct, text):
    tokens = tl_tokenizer(text + punct + punct + punct)
    assert len(tokens) == 4
    assert tokens[0].text == text
    assert tokens[1].text == punct


@pytest.mark.parametrize("text", ["'Ang"])
def test_tl_tokenizer_splits_open_apostrophe(tl_tokenizer, text):
    tokens = tl_tokenizer(text)
    assert len(tokens) == 2
    assert tokens[0].text == "'"


@pytest.mark.parametrize("text", ["Mabuhay''"])
def test_tl_tokenizer_splits_double_end_quote(tl_tokenizer, text):
    tokens = tl_tokenizer(text)
    assert len(tokens) == 2
    tokens_punct = tl_tokenizer("''")
    assert len(tokens_punct) == 1


@pytest.mark.parametrize("punct_open,punct_close", PUNCT_PAIRED)
@pytest.mark.parametrize("text", ["Mabuhay"])
def test_tl_tokenizer_splits_open_close_punct(
    tl_tokenizer, punct_open, punct_close, text
):
    tokens = tl_tokenizer(punct_open + text + punct_close)
    assert len(tokens) == 3
    assert tokens[0].text == punct_open
    assert tokens[1].text == text
    assert tokens[2].text == punct_close


@pytest.mark.parametrize("punct_open,punct_close", PUNCT_PAIRED)
@pytest.mark.parametrize("punct_open2,punct_close2", [("`", "'")])
@pytest.mark.parametrize("text", ["Mabuhay"])
def test_tl_tokenizer_two_diff_punct(
    tl_tokenizer, punct_open, punct_close, punct_open2, punct_close2, text
):
    tokens = tl_tokenizer(punct_open2 + punct_open + text + punct_close + punct_close2)
    assert len(tokens) == 5
    assert tokens[0].text == punct_open2
    assert tokens[1].text == punct_open
    assert tokens[2].text == text
    assert tokens[3].text == punct_close
    assert tokens[4].text == punct_close2


@pytest.mark.parametrize("text,punct", [("(sa'yo", "(")])
def test_tl_tokenizer_splits_pre_punct_regex(text, punct):
    tl_search_prefixes = compile_prefix_regex(TOKENIZER_PREFIXES).search
    match = tl_search_prefixes(text)
    assert match.group() == punct


def test_tl_tokenizer_splits_bracket_period(tl_tokenizer):
    text = "(Dumating siya kahapon)."
    tokens = tl_tokenizer(text)
    assert tokens[len(tokens) - 1].text == "."

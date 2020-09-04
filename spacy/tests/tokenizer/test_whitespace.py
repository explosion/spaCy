import pytest


@pytest.mark.parametrize("text", ["lorem ipsum"])
def test_tokenizer_splits_single_space(tokenizer, text):
    tokens = tokenizer(text)
    assert len(tokens) == 2


@pytest.mark.parametrize("text", ["lorem  ipsum"])
def test_tokenizer_splits_double_space(tokenizer, text):
    tokens = tokenizer(text)
    assert len(tokens) == 3
    assert tokens[1].text == " "


@pytest.mark.parametrize("text", ["lorem ipsum  "])
def test_tokenizer_handles_double_trailing_ws(tokenizer, text):
    tokens = tokenizer(text)
    assert repr(tokens.text_with_ws) == repr(text)


@pytest.mark.parametrize("text", ["lorem\nipsum"])
def test_tokenizer_splits_newline(tokenizer, text):
    tokens = tokenizer(text)
    assert len(tokens) == 3
    assert tokens[1].text == "\n"


@pytest.mark.parametrize("text", ["lorem \nipsum"])
def test_tokenizer_splits_newline_space(tokenizer, text):
    tokens = tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["lorem  \nipsum"])
def test_tokenizer_splits_newline_double_space(tokenizer, text):
    tokens = tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["lorem \n ipsum"])
def test_tokenizer_splits_newline_space_wrap(tokenizer, text):
    tokens = tokenizer(text)
    assert len(tokens) == 3

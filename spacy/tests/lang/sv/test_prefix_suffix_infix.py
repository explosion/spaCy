import pytest


@pytest.mark.parametrize("text", ["(under)"])
def test_tokenizer_splits_no_special(sv_tokenizer, text):
    tokens = sv_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["gitta'r", "Björn's", "Lars'"])
def test_tokenizer_handles_no_punct(sv_tokenizer, text):
    tokens = sv_tokenizer(text)
    assert len(tokens) == 1


@pytest.mark.parametrize("text", ["svart.Gul", "Hej.Världen"])
def test_tokenizer_splits_period_infix(sv_tokenizer, text):
    tokens = sv_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["Hej,Världen", "en,två"])
def test_tokenizer_splits_comma_infix(sv_tokenizer, text):
    tokens = sv_tokenizer(text)
    assert len(tokens) == 3
    assert tokens[0].text == text.split(",")[0]
    assert tokens[1].text == ","
    assert tokens[2].text == text.split(",")[1]


@pytest.mark.parametrize("text", ["svart...Gul", "svart...gul"])
def test_tokenizer_splits_ellipsis_infix(sv_tokenizer, text):
    tokens = sv_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.issue(12311)
@pytest.mark.parametrize("text", ["99:e", "c:a", "EU:s", "Maj:t"])
def test_sv_tokenizer_handles_colon(sv_tokenizer, text):
    tokens = sv_tokenizer(text)
    assert len(tokens) == 1

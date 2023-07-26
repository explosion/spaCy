from string import punctuation

import pytest

PUNCT_OPEN = ["(", "[", "{", "*"]
PUNCT_CLOSE = [")", "]", "}", "*"]
PUNCT_PAIRED = [("(", ")"), ("[", "]"), ("{", "}"), ("*", "*")]


@pytest.mark.parametrize("text", ["(", "((", "<"])
def test_ru_tokenizer_handles_only_punct(ru_tokenizer, text):
    tokens = ru_tokenizer(text)
    assert len(tokens) == len(text)


@pytest.mark.parametrize("punct", PUNCT_OPEN)
@pytest.mark.parametrize("text", ["Привет"])
def test_ru_tokenizer_splits_open_punct(ru_tokenizer, punct, text):
    tokens = ru_tokenizer(punct + text)
    assert len(tokens) == 2
    assert tokens[0].text == punct
    assert tokens[1].text == text


@pytest.mark.parametrize("punct", PUNCT_CLOSE)
@pytest.mark.parametrize("text", ["Привет"])
def test_ru_tokenizer_splits_close_punct(ru_tokenizer, punct, text):
    tokens = ru_tokenizer(text + punct)
    assert len(tokens) == 2
    assert tokens[0].text == text
    assert tokens[1].text == punct


@pytest.mark.parametrize("punct", PUNCT_OPEN)
@pytest.mark.parametrize("punct_add", ["`"])
@pytest.mark.parametrize("text", ["Привет"])
def test_ru_tokenizer_splits_two_diff_open_punct(ru_tokenizer, punct, punct_add, text):
    tokens = ru_tokenizer(punct + punct_add + text)
    assert len(tokens) == 3
    assert tokens[0].text == punct
    assert tokens[1].text == punct_add
    assert tokens[2].text == text


@pytest.mark.parametrize("punct", PUNCT_CLOSE)
@pytest.mark.parametrize("punct_add", ["'"])
@pytest.mark.parametrize("text", ["Привет"])
def test_ru_tokenizer_splits_two_diff_close_punct(ru_tokenizer, punct, punct_add, text):
    tokens = ru_tokenizer(text + punct + punct_add)
    assert len(tokens) == 3
    assert tokens[0].text == text
    assert tokens[1].text == punct
    assert tokens[2].text == punct_add


@pytest.mark.parametrize("punct", PUNCT_OPEN)
@pytest.mark.parametrize("text", ["Привет"])
def test_ru_tokenizer_splits_same_open_punct(ru_tokenizer, punct, text):
    tokens = ru_tokenizer(punct + punct + punct + text)
    assert len(tokens) == 4
    assert tokens[0].text == punct
    assert tokens[3].text == text


@pytest.mark.parametrize("punct", PUNCT_CLOSE)
@pytest.mark.parametrize("text", ["Привет"])
def test_ru_tokenizer_splits_same_close_punct(ru_tokenizer, punct, text):
    tokens = ru_tokenizer(text + punct + punct + punct)
    assert len(tokens) == 4
    assert tokens[0].text == text
    assert tokens[1].text == punct


@pytest.mark.parametrize("text", ["'Тест"])
def test_ru_tokenizer_splits_open_appostrophe(ru_tokenizer, text):
    tokens = ru_tokenizer(text)
    assert len(tokens) == 2
    assert tokens[0].text == "'"


@pytest.mark.parametrize("text", ["Тест''"])
def test_ru_tokenizer_splits_double_end_quote(ru_tokenizer, text):
    tokens = ru_tokenizer(text)
    assert len(tokens) == 2
    tokens_punct = ru_tokenizer("''")
    assert len(tokens_punct) == 1


@pytest.mark.parametrize("punct_open,punct_close", PUNCT_PAIRED)
@pytest.mark.parametrize("text", ["Тест"])
def test_ru_tokenizer_splits_open_close_punct(
    ru_tokenizer, punct_open, punct_close, text
):
    tokens = ru_tokenizer(punct_open + text + punct_close)
    assert len(tokens) == 3
    assert tokens[0].text == punct_open
    assert tokens[1].text == text
    assert tokens[2].text == punct_close


@pytest.mark.parametrize("punct_open,punct_close", PUNCT_PAIRED)
@pytest.mark.parametrize("punct_open2,punct_close2", [("`", "'")])
@pytest.mark.parametrize("text", ["Тест"])
def test_ru_tokenizer_two_diff_punct(
    ru_tokenizer, punct_open, punct_close, punct_open2, punct_close2, text
):
    tokens = ru_tokenizer(punct_open2 + punct_open + text + punct_close + punct_close2)
    assert len(tokens) == 5
    assert tokens[0].text == punct_open2
    assert tokens[1].text == punct_open
    assert tokens[2].text == text
    assert tokens[3].text == punct_close
    assert tokens[4].text == punct_close2


@pytest.mark.parametrize("text", ["Тест."])
def test_ru_tokenizer_splits_trailing_dot(ru_tokenizer, text):
    tokens = ru_tokenizer(text)
    assert tokens[1].text == "."


def test_ru_tokenizer_splits_bracket_period(ru_tokenizer):
    text = "(Раз, два, три, проверка)."
    tokens = ru_tokenizer(text)
    assert tokens[len(tokens) - 1].text == "."


@pytest.mark.parametrize(
    "text",
    [
        "рекоменду́я подда́ть жару́. Самого́ Баргамота",
        "РЕКОМЕНДУ́Я ПОДДА́ТЬ ЖАРУ́. САМОГО́ БАРГАМОТА",
        "рекоменду̍я подда̍ть жару̍.Самого̍ Баргамота",
        "рекоменду̍я подда̍ть жару̍.'Самого̍ Баргамота",
        "рекоменду̍я подда̍ть жару̍,самого̍ Баргамота",
        "рекоменду̍я подда̍ть жару̍:самого̍ Баргамота",
        "рекоменду̍я подда̍ть жару̍. самого̍ Баргамота",
        "рекоменду̍я подда̍ть жару̍, самого̍ Баргамота",
        "рекоменду̍я подда̍ть жару̍: самого̍ Баргамота",
        "рекоменду̍я подда̍ть жару̍-самого̍ Баргамота",
    ],
)
def test_ru_tokenizer_handles_final_diacritics(ru_tokenizer, text):
    tokens = ru_tokenizer(text)
    assert tokens[2].text in ("жару́", "ЖАРУ́", "жару̍")
    assert tokens[3].text in punctuation


@pytest.mark.parametrize(
    "text",
    [
        "РЕКОМЕНДУ́Я ПОДДА́ТЬ ЖАРУ́.САМОГО́ БАРГАМОТА",
        "рекоменду̍я подда̍ть жару́.самого́ Баргамота",
    ],
)
def test_ru_tokenizer_handles_final_diacritic_and_period(ru_tokenizer, text):
    tokens = ru_tokenizer(text)
    assert tokens[2].text.lower() == "жару́.самого́"

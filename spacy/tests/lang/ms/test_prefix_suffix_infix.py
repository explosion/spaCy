import pytest


@pytest.mark.parametrize("text", ["(Ma'arif)"])
def test_ms_tokenizer_splits_no_special(id_tokenizer, text):
    tokens = id_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["Ma'arif"])
def test_ms_tokenizer_splits_no_punct(id_tokenizer, text):
    tokens = id_tokenizer(text)
    assert len(tokens) == 1


@pytest.mark.parametrize("text", ["(Ma'arif"])
def test_ms_tokenizer_splits_prefix_punct(id_tokenizer, text):
    tokens = id_tokenizer(text)
    assert len(tokens) == 2


@pytest.mark.parametrize("text", ["Ma'arif)"])
def test_ms_tokenizer_splits_suffix_punct(id_tokenizer, text):
    tokens = id_tokenizer(text)
    assert len(tokens) == 2


@pytest.mark.parametrize("text", ["(Ma'arif)"])
def test_ms_tokenizer_splits_even_wrap(id_tokenizer, text):
    tokens = id_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["(Ma'arif?)"])
def test_tokenizer_splits_uneven_wrap(id_tokenizer, text):
    tokens = id_tokenizer(text)
    assert len(tokens) == 4


@pytest.mark.parametrize("text,length", [("S.Kom.", 1), ("SKom.", 2), ("(S.Kom.", 2)])
def test_ms_tokenizer_splits_prefix_interact(id_tokenizer, text, length):
    tokens = id_tokenizer(text)
    assert len(tokens) == length


@pytest.mark.parametrize("text", ["S.Kom.)"])
def test_ms_tokenizer_splits_suffix_interact(id_tokenizer, text):
    tokens = id_tokenizer(text)
    assert len(tokens) == 2


@pytest.mark.parametrize("text", ["(S.Kom.)"])
def test_ms_tokenizer_splits_even_wrap_interact(id_tokenizer, text):
    tokens = id_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["(S.Kom.?)"])
def test_ms_tokenizer_splits_uneven_wrap_interact(id_tokenizer, text):
    tokens = id_tokenizer(text)
    assert len(tokens) == 4


@pytest.mark.parametrize(
    "text,length",
    [("kerana", 1), ("Mahathir-Anwar", 3), ("Tun Dr. Ismail-Abdul Rahman", 6)],
)
def test_my_tokenizer_splits_hyphens(ms_tokenizer, text, length):
    tokens = ms_tokenizer(text)
    assert len(tokens) == length


@pytest.mark.parametrize("text", ["0.1-13.5", "0.0-0.1", "103.27-300"])
def test_ms_tokenizer_splits_numeric_range(id_tokenizer, text):
    tokens = id_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["ini.Sani", "Halo.Malaysia"])
def test_ms_tokenizer_splits_period_infix(id_tokenizer, text):
    tokens = id_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["Halo,Malaysia", "satu,dua"])
def test_ms_tokenizer_splits_comma_infix(id_tokenizer, text):
    tokens = id_tokenizer(text)
    assert len(tokens) == 3
    assert tokens[0].text == text.split(",")[0]
    assert tokens[1].text == ","
    assert tokens[2].text == text.split(",")[1]


@pytest.mark.parametrize("text", ["halo...Malaysia", "dia...pergi"])
def test_ms_tokenizer_splits_ellipsis_infix(id_tokenizer, text):
    tokens = id_tokenizer(text)
    assert len(tokens) == 3


def test_ms_tokenizer_splits_double_hyphen_infix(id_tokenizer):
    tokens = id_tokenizer("Arsene Wenger--pengurus Arsenal--mengadakan sidang media.")
    assert len(tokens) == 10
    assert tokens[0].text == "Arsene"
    assert tokens[1].text == "Wenger"
    assert tokens[2].text == "--"
    assert tokens[3].text == "pengurus"
    assert tokens[4].text == "Arsenal"
    assert tokens[5].text == "--"
    assert tokens[6].text == "mengadakan"
    assert tokens[7].text == "sidang"
    assert tokens[8].text == "media"
    assert tokens[9].text == "."

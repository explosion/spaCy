import pytest


@pytest.mark.parametrize("text", ["(Ma'arif)"])
def test_id_tokenizer_splits_no_special(id_tokenizer, text):
    tokens = id_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["Ma'arif"])
def test_id_tokenizer_splits_no_punct(id_tokenizer, text):
    tokens = id_tokenizer(text)
    assert len(tokens) == 1


@pytest.mark.parametrize("text", ["(Ma'arif"])
def test_id_tokenizer_splits_prefix_punct(id_tokenizer, text):
    tokens = id_tokenizer(text)
    assert len(tokens) == 2


@pytest.mark.parametrize("text", ["Ma'arif)"])
def test_id_tokenizer_splits_suffix_punct(id_tokenizer, text):
    tokens = id_tokenizer(text)
    assert len(tokens) == 2


@pytest.mark.parametrize("text", ["(Ma'arif)"])
def test_id_tokenizer_splits_even_wrap(id_tokenizer, text):
    tokens = id_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["(Ma'arif?)"])
def test_tokenizer_splits_uneven_wrap(id_tokenizer, text):
    tokens = id_tokenizer(text)
    assert len(tokens) == 4


@pytest.mark.parametrize("text,length", [("S.Kom.", 1), ("SKom.", 2), ("(S.Kom.", 2)])
def test_id_tokenizer_splits_prefix_interact(id_tokenizer, text, length):
    tokens = id_tokenizer(text)
    assert len(tokens) == length


@pytest.mark.parametrize("text", ["S.Kom.)"])
def test_id_tokenizer_splits_suffix_interact(id_tokenizer, text):
    tokens = id_tokenizer(text)
    assert len(tokens) == 2


@pytest.mark.parametrize("text", ["(S.Kom.)"])
def test_id_tokenizer_splits_even_wrap_interact(id_tokenizer, text):
    tokens = id_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["(S.Kom.?)"])
def test_id_tokenizer_splits_uneven_wrap_interact(id_tokenizer, text):
    tokens = id_tokenizer(text)
    assert len(tokens) == 4


@pytest.mark.parametrize(
    "text,length", [("gara-gara", 1), ("Jokowi-Ahok", 3), ("Sukarno-Hatta", 3)]
)
def test_id_tokenizer_splits_hyphens(id_tokenizer, text, length):
    tokens = id_tokenizer(text)
    assert len(tokens) == length


@pytest.mark.parametrize("text", ["0.1-13.5", "0.0-0.1", "103.27-300"])
def test_id_tokenizer_splits_numeric_range(id_tokenizer, text):
    tokens = id_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["ini.Budi", "Halo.Bandung"])
def test_id_tokenizer_splits_period_infix(id_tokenizer, text):
    tokens = id_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["Halo,Bandung", "satu,dua"])
def test_id_tokenizer_splits_comma_infix(id_tokenizer, text):
    tokens = id_tokenizer(text)
    assert len(tokens) == 3
    assert tokens[0].text == text.split(",")[0]
    assert tokens[1].text == ","
    assert tokens[2].text == text.split(",")[1]


@pytest.mark.parametrize("text", ["halo...Bandung", "dia...pergi"])
def test_id_tokenizer_splits_ellipsis_infix(id_tokenizer, text):
    tokens = id_tokenizer(text)
    assert len(tokens) == 3


def test_id_tokenizer_splits_double_hyphen_infix(id_tokenizer):
    tokens = id_tokenizer("Arsene Wenger--manajer Arsenal--melakukan konferensi pers.")
    assert len(tokens) == 10
    assert tokens[0].text == "Arsene"
    assert tokens[1].text == "Wenger"
    assert tokens[2].text == "--"
    assert tokens[3].text == "manajer"
    assert tokens[4].text == "Arsenal"
    assert tokens[5].text == "--"
    assert tokens[6].text == "melakukan"
    assert tokens[7].text == "konferensi"
    assert tokens[8].text == "pers"
    assert tokens[9].text == "."

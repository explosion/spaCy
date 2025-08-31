import pytest


@pytest.mark.parametrize("text", ["(ka)"])
def test_ht_tokenizer_splits_no_special(ht_tokenizer, text):
    tokens = ht_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["m'ap"])
def test_ht_tokenizer_splits_no_punct(ht_tokenizer, text):
    tokens = ht_tokenizer(text)
    assert len(tokens) == 2


@pytest.mark.parametrize("text", ["(m'ap"])
def test_ht_tokenizer_splits_prefix_punct(ht_tokenizer, text):
    tokens = ht_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["m'ap)"])
def test_ht_tokenizer_splits_suffix_punct(ht_tokenizer, text):
    tokens = ht_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["(m'ap)"])
def test_ht_tokenizer_splits_even_wrap(ht_tokenizer, text):
    tokens = ht_tokenizer(text)
    assert len(tokens) == 4


@pytest.mark.parametrize("text", ["(m'ap?)"])
def test_ht_tokenizer_splits_uneven_wrap(ht_tokenizer, text):
    tokens = ht_tokenizer(text)
    assert len(tokens) == 5


@pytest.mark.parametrize(
    "text,length", [("Ozetazini.", 2), ("Frans.", 2), ("(Ozetazini.", 3)]
)
def test_ht_tokenizer_splits_prefix_interact(ht_tokenizer, text, length):
    tokens = ht_tokenizer(text)
    assert len(tokens) == length


@pytest.mark.parametrize("text", ["Ozetazini.)"])
def test_ht_tokenizer_splits_suffix_interact(ht_tokenizer, text):
    tokens = ht_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["(Ozetazini.)"])
def test_ht_tokenizer_splits_even_wrap_interact(ht_tokenizer, text):
    tokens = ht_tokenizer(text)
    assert len(tokens) == 4


@pytest.mark.parametrize("text", ["(Ozetazini?)"])
def test_ht_tokenizer_splits_uneven_wrap_interact(ht_tokenizer, text):
    tokens = ht_tokenizer(text)
    assert len(tokens) == 4


@pytest.mark.parametrize("text", ["pi-bon"])
def test_ht_tokenizer_splits_hyphens(ht_tokenizer, text):
    tokens = ht_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["0.1-13.5", "0.0-0.1", "103.27-300"])
def test_ht_tokenizer_splits_numeric_range(ht_tokenizer, text):
    tokens = ht_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["pi.Bon", "Bon.Jour"])
def test_ht_tokenizer_splits_period_infix(ht_tokenizer, text):
    tokens = ht_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize("text", ["Bonjou,moun", "youn,de"])
def test_ht_tokenizer_splits_comma_infix(ht_tokenizer, text):
    tokens = ht_tokenizer(text)
    assert len(tokens) == 3
    assert tokens[0].text == text.split(",")[0]
    assert tokens[1].text == ","
    assert tokens[2].text == text.split(",")[1]


@pytest.mark.parametrize("text", ["pi...Bon", "pi...bon"])
def test_ht_tokenizer_splits_ellipsis_infix(ht_tokenizer, text):
    tokens = ht_tokenizer(text)
    assert len(tokens) == 3


def test_ht_tokenizer_splits_double_hyphen_infix(ht_tokenizer):
    tokens = ht_tokenizer("Pa vrè--men ou konnen--mwen renmen w.")
    assert tokens[0].text == "Pa"
    assert tokens[1].text == "vrè"
    assert tokens[2].text == "--"
    assert tokens[3].text == "men"
    assert tokens[4].text == "ou"
    assert tokens[5].text == "konnen"
    assert tokens[6].text == "--"
    assert tokens[7].text == "mwen"
    assert tokens[8].text == "renmen"
    assert tokens[9].text == "w"
    assert tokens[10].text == "."


def test_ht_tokenizer_splits_period_abbr(ht_tokenizer):
    text = "Jodi a se Madi.Mr."
    tokens = ht_tokenizer(text)
    assert len(tokens) == 7
    assert tokens[0].text == "Jodi"
    assert tokens[1].text == "a"
    assert tokens[2].text == "se"
    assert tokens[3].text == "Madi"
    assert tokens[4].text == "."
    assert tokens[5].text == "Mr"
    assert tokens[6].text == "."


def test_ht_tokenizer_splits_paren_period(ht_tokenizer):
    tokens = ht_tokenizer("M ap teste sa (pou kounye a).")
    words = [t.text for t in tokens]
    assert "a" in words
    assert ")" in words
    assert "." in words

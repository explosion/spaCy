import pytest


@pytest.mark.parametrize(
    "text,expected",
    [
        ("f'annwylyd", ["f'", "annwylyd"]),
        ("d'eisiau", ["d'", "eisiau"]),
        ("F'enaid", ["F'", "enaid"]),
        ("f’annwylyd", ["f’", "annwylyd"]),
    ],
)
def test_cy_tokenizer_splits_clitic_prefix(cy_tokenizer, text, expected):
    tokens = cy_tokenizer(text)
    assert [t.text for t in tokens] == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("i'r", ["i", "'r"]),
        ("o'r", ["o", "'r"]),
        ("Mae'r", ["Mae", "'r"]),
        ("i'n", ["i", "'n"]),
        ("a'i", ["a", "'i"]),
        ("a'u", ["a", "'u"]),
        ("a'm", ["a", "'m"]),
        ("i'ch", ["i", "'ch"]),
        ("i'th", ["i", "'th"]),
        ("i'w", ["i", "'w"]),
        ("i’r", ["i", "’r"]),
        ("A’U", ["A", "’U"]),
    ],
)
def test_cy_tokenizer_splits_clitic_suffix(cy_tokenizer, text, expected):
    tokens = cy_tokenizer(text)
    assert [t.text for t in tokens] == expected


@pytest.mark.parametrize(
    "text", ["cyd-destun", "hunan-barch", "Ynys-y-bwl", "ôl-ddoethurol"]
)
def test_cy_tokenizer_keeps_hyphenated_word(cy_tokenizer, text):
    tokens = cy_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].text == text


@pytest.mark.parametrize(
    "text,expected", [("1-2", ["1", "-", "2"]), ("10-15", ["10", "-", "15"])]
)
def test_cy_tokenizer_splits_hyphen_between_digits(cy_tokenizer, text, expected):
    tokens = cy_tokenizer(text)
    assert [t.text for t in tokens] == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("(i'r", ["(", "i", "'r"]),
        ("i'r)", ["i", "'r", ")"]),
        ("(i'r)", ["(", "i", "'r", ")"]),
        ("(cyd-destun)", ["(", "cyd-destun", ")"]),
        ("'r", ["'r"]),
    ],
)
def test_cy_tokenizer_splits_wrapping_punct(cy_tokenizer, text, expected):
    tokens = cy_tokenizer(text)
    assert [t.text for t in tokens] == expected

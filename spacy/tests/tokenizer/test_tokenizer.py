import pytest
from spacy.vocab import Vocab
from spacy.tokenizer import Tokenizer
from spacy.util import ensure_path


def test_tokenizer_handles_no_word(tokenizer):
    tokens = tokenizer("")
    assert len(tokens) == 0


@pytest.mark.parametrize("text", ["lorem"])
def test_tokenizer_handles_single_word(tokenizer, text):
    tokens = tokenizer(text)
    assert tokens[0].text == text


def test_tokenizer_handles_punct(tokenizer):
    text = "Lorem, ipsum."
    tokens = tokenizer(text)
    assert len(tokens) == 4
    assert tokens[0].text == "Lorem"
    assert tokens[1].text == ","
    assert tokens[2].text == "ipsum"
    assert tokens[1].text != "Lorem"


def test_tokenizer_handles_punct_braces(tokenizer):
    text = "Lorem, (ipsum)."
    tokens = tokenizer(text)
    assert len(tokens) == 6


def test_tokenizer_handles_digits(tokenizer):
    exceptions = ["hu", "bn"]
    text = "Lorem ipsum: 1984."
    tokens = tokenizer(text)

    if tokens[0].lang_ not in exceptions:
        assert len(tokens) == 5
        assert tokens[0].text == "Lorem"
        assert tokens[3].text == "1984"


@pytest.mark.parametrize(
    "text",
    ["google.com", "python.org", "spacy.io", "explosion.ai", "http://www.google.com"],
)
def test_tokenizer_keep_urls(tokenizer, text):
    tokens = tokenizer(text)
    assert len(tokens) == 1


@pytest.mark.parametrize("text", ["NASDAQ:GOOG"])
def test_tokenizer_colons(tokenizer, text):
    tokens = tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize(
    "text", ["hello123@example.com", "hi+there@gmail.it", "matt@explosion.ai"]
)
def test_tokenizer_keeps_email(tokenizer, text):
    tokens = tokenizer(text)
    assert len(tokens) == 1


def test_tokenizer_handles_long_text(tokenizer):
    text = """Lorem ipsum dolor sit amet, consectetur adipiscing elit

Cras egestas orci non porttitor maximus.
Maecenas quis odio id dolor rhoncus dignissim. Curabitur sed velit at orci ultrices sagittis. Nulla commodo euismod arcu eget vulputate.

Phasellus tincidunt, augue quis porta finibus, massa sapien consectetur augue, non lacinia enim nibh eget ipsum. Vestibulum in bibendum mauris.

"Nullam porta fringilla enim, a dictum orci consequat in." Mauris nec malesuada justo."""

    tokens = tokenizer(text)
    assert len(tokens) > 5


@pytest.mark.parametrize("file_name", ["sun.txt"])
def test_tokenizer_handle_text_from_file(tokenizer, file_name):
    loc = ensure_path(__file__).parent / file_name
    text = loc.open("r", encoding="utf8").read()
    assert len(text) != 0
    tokens = tokenizer(text)
    assert len(tokens) > 100


def test_tokenizer_suspected_freeing_strings(tokenizer):
    text1 = "Lorem dolor sit amet, consectetur adipiscing elit."
    text2 = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    tokens1 = tokenizer(text1)
    tokens2 = tokenizer(text2)
    assert tokens1[0].text == "Lorem"
    assert tokens2[0].text == "Lorem"


@pytest.mark.parametrize("text,tokens", [("lorem", [{"orth": "lo"}, {"orth": "rem"}])])
def test_tokenizer_add_special_case(tokenizer, text, tokens):
    tokenizer.add_special_case(text, tokens)
    doc = tokenizer(text)
    assert doc[0].text == tokens[0]["orth"]
    assert doc[1].text == tokens[1]["orth"]


@pytest.mark.parametrize(
    "text,tokens",
    [
        ("lorem", [{"orth": "lo"}, {"orth": "re"}]),
        ("lorem", [{"orth": "lo", "tag": "A"}, {"orth": "rem"}]),
    ],
)
def test_tokenizer_validate_special_case(tokenizer, text, tokens):
    with pytest.raises(ValueError):
        tokenizer.add_special_case(text, tokens)


@pytest.mark.parametrize(
    "text,tokens", [("lorem", [{"orth": "lo", "norm": "LO"}, {"orth": "rem"}])]
)
def test_tokenizer_add_special_case_tag(text, tokens):
    vocab = Vocab()
    tokenizer = Tokenizer(vocab, {}, None, None, None)
    tokenizer.add_special_case(text, tokens)
    doc = tokenizer(text)
    assert doc[0].text == tokens[0]["orth"]
    assert doc[0].norm_ == tokens[0]["norm"]
    assert doc[1].text == tokens[1]["orth"]


def test_tokenizer_special_cases_with_affixes(tokenizer):
    text = '(((_SPECIAL_ A/B, A/B-A/B")'
    tokenizer.add_special_case("_SPECIAL_", [{"orth": "_SPECIAL_"}])
    tokenizer.add_special_case("A/B", [{"orth": "A/B"}])
    doc = tokenizer(text)
    assert [token.text for token in doc] == [
        "(",
        "(",
        "(",
        "_SPECIAL_",
        "A/B",
        ",",
        "A/B",
        "-",
        "A/B",
        '"',
        ")",
    ]


def test_tokenizer_special_cases_with_period(tokenizer):
    text = "_SPECIAL_."
    tokenizer.add_special_case("_SPECIAL_", [{"orth": "_SPECIAL_"}])
    doc = tokenizer(text)
    assert [token.text for token in doc] == ["_SPECIAL_", "."]


def test_tokenizer_special_cases_idx(tokenizer):
    text = "the _ID'X_"
    tokenizer.add_special_case("_ID'X_", [{"orth": "_ID"}, {"orth": "'X_"}])
    doc = tokenizer(text)
    assert doc[1].idx == 4
    assert doc[2].idx == 7

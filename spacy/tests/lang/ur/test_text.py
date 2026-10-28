import pytest


def test_ur_tokenizer_handles_long_text(ur_tokenizer):
    text = """اصل میں، رسوا ہونے کی ہمیں کچھ عادت سی ہو گئی ہے۔"""
    tokens = ur_tokenizer(text)
    assert len(tokens) == 14


@pytest.mark.parametrize("text,length", [("تحریر باسط حبیب", 3), ("میرا پاکستان", 2)])
def test_ur_tokenizer_handles_cnts(ur_tokenizer, text, length):
    tokens = ur_tokenizer(text)
    assert len(tokens) == length


@pytest.mark.parametrize(
    "text",
    [
        "اصل میں، رسوا ہونے کی ہمیں کچھ عادت سی ہو گئی ہے۔",
        "کیا آپ 18 یا اٹھارہ سال کے ہیں؟",
        "hello\tاردو\nline",
        "email@example.com اور https://spacy.io",
        "لفظ۔لفظ",
        "خان (وزیر) نے کہا۔",
        "«اردو» اور “انگریزی”",
        "یہ🙂جملہ",
        "ہےً۔",
        "می\u200cں",
        "\u200fاردو\u200e",
        "قیســــم",
        "Rs. 50 اور ۵۰٪",
        "Dr. Khan اور U.S. میں",
        "ہےً۔کیا",
        "1،2 اور 1,000",
        "«لفظً۔لفظ»",
    ],
)
def test_ur_tokenizer_preserves_text_and_offsets(ur_tokenizer, text):
    doc = ur_tokenizer(text)
    assert doc.text == text
    assert "".join(token.text_with_ws for token in doc) == text
    for token in doc:
        assert text[token.idx : token.idx + len(token)] == token.text


@pytest.mark.parametrize(
    "text,punct",
    [
        ("ہے۔", "۔"),
        ("ہیں؟", "؟"),
        ("میں،", "،"),
        ("خان؛", "؛"),
    ],
)
def test_ur_tokenizer_splits_trailing_punct(ur_tokenizer, text, punct):
    tokens = ur_tokenizer(text)
    assert len(tokens) == 2
    assert tokens[1].text == punct


def test_ur_tokenizer_splits_unspaced_urdu_punct(ur_tokenizer):
    tokens = ur_tokenizer("لفظ۔لفظ")
    assert [token.text for token in tokens] == ["لفظ", "۔", "لفظ"]


def test_ur_tokenizer_keeps_latin_abbreviation(ur_tokenizer):
    tokens = ur_tokenizer("Dr. خان")
    assert tokens[0].text == "Dr."


def test_ur_tokenizer_keeps_url_and_email(ur_tokenizer):
    tokens = ur_tokenizer("info@example.com https://spacy.io")
    assert tokens[0].like_email
    assert tokens[1].like_url


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Dr.", ["Dr."]),
        ("(Dr. Khan)", ["(", "Dr.", "Khan", ")"]),
        ("Dr.,", ["Dr.", ","]),
        ("ص.ب", ["ص.ب"]),
        ("(ص.ب)", ["(", "ص.ب", ")"]),
    ],
)
def test_ur_abbreviation_contexts(ur_tokenizer, text, expected):
    tokens = ur_tokenizer(text)
    assert [token.text for token in tokens] == expected


def test_ur_ellipsis_is_one_token(ur_tokenizer):
    tokens = ur_tokenizer("خان۔۔۔اب")
    assert [token.text for token in tokens] == ["خان", "۔۔۔", "اب"]
    tokens = ur_tokenizer("یہ۔۔وہ")
    assert [token.text for token in tokens] == ["یہ", "۔۔", "وہ"]


def test_ur_single_period_is_not_ellipsis(ur_tokenizer):
    tokens = ur_tokenizer("یہ۔ وہ۔")
    assert [token.text for token in tokens] == ["یہ", "۔", "وہ", "۔"]


def test_ur_tokenizer_handles_long_punct_sequence(ur_tokenizer):
    text = "لفظ۔" * 2000
    doc = ur_tokenizer(text)
    assert doc.text == text
    assert len(doc) == 4000
    assert doc[0].text == "لفظ"
    assert doc[1].text == "۔"


@pytest.mark.parametrize(
    "word",
    ["کا", "کو", "سے", "میں", "نے", "وہ", "یہ", "اور", "ہے", "نہیں"],
)
def test_ur_is_stop_standard_function_words(ur_tokenizer, word):
    tokens = ur_tokenizer(word)
    assert tokens[0].is_stop

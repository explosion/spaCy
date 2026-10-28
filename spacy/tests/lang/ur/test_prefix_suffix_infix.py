import pytest

from spacy.lang.punctuation import TOKENIZER_INFIXES as BASE_INFIXES
from spacy.lang.punctuation import TOKENIZER_PREFIXES as BASE_PREFIXES
from spacy.lang.punctuation import TOKENIZER_SUFFIXES as BASE_SUFFIXES
from spacy.lang.tokenizer_exceptions import BASE_EXCEPTIONS
from spacy.lang.ur.punctuation import TOKENIZER_INFIXES
from spacy.lang.ur.punctuation import TOKENIZER_PREFIXES
from spacy.lang.ur.punctuation import TOKENIZER_SUFFIXES
from spacy.lang.ur.tokenizer_exceptions import TOKENIZER_EXCEPTIONS


def test_ur_tokenizer_tables_are_copies():
    assert TOKENIZER_INFIXES is not BASE_INFIXES
    assert TOKENIZER_PREFIXES is not BASE_PREFIXES
    assert TOKENIZER_SUFFIXES is not BASE_SUFFIXES
    assert TOKENIZER_EXCEPTIONS is not BASE_EXCEPTIONS
    assert r"۔۔+" not in BASE_INFIXES
    assert "Dr." in TOKENIZER_EXCEPTIONS
    assert "Dr." not in BASE_EXCEPTIONS


@pytest.mark.parametrize("text", ["ہےں۔", "کیا۔"])
def test_contractions(ur_tokenizer, text):
    """Test specific Urdu punctuation character"""
    tokens = ur_tokenizer(text)
    assert len(tokens) == 2


@pytest.mark.parametrize(
    "text,expected",
    [
        ("لفظ؟لفظ", ["لفظ", "؟", "لفظ"]),
        ("لفظ،لفظ", ["لفظ", "،", "لفظ"]),
        ("لفظ؛لفظ", ["لفظ", "؛", "لفظ"]),
        ("خان۔۔۔اب", ["خان", "۔۔۔", "اب"]),
        ("ہےً۔کیا", ["ہےً", "۔", "کیا"]),
        ("لفظً۔لفظ", ["لفظً", "۔", "لفظ"]),
        ("«لفظ۔لفظ»", ["«", "لفظ", "۔", "لفظ", "»"]),
        ("لفظً۔»", ["لفظً", "۔", "»"]),
        ("1،2", ["1", "،", "2"]),
        ("۱،۲", ["۱", "،", "۲"]),
        ("1,000", ["1,000"]),
        ("۱٬۰۰۰", ["۱٬۰۰۰"]),
        ("۳٫۱۴", ["۳٫۱۴"]),
    ],
)
def test_ur_infix_punct_without_space(ur_tokenizer, text, expected):
    tokens = ur_tokenizer(text)
    assert [token.text for token in tokens] == expected


def test_ur_suffix_splits_arabic_indic_percent(ur_tokenizer):
    tokens = ur_tokenizer("۵۰٪")
    assert [token.text for token in tokens] == ["۵۰", "٪"]
    assert tokens[0].like_num


@pytest.mark.parametrize(
    "text,expected",
    [
        ("50%", ["50", "%"]),
        ("50+", ["50", "+"]),
        ("۱۸٪", ["۱۸", "٪"]),
        ("١٨٪", ["١٨", "٪"]),
    ],
)
def test_ur_suffix_splits_percent_and_plus(ur_tokenizer, text, expected):
    tokens = ur_tokenizer(text)
    assert [token.text for token in tokens] == expected
    assert tokens[0].like_num


def test_ur_grouped_number_stays_one_token(ur_tokenizer):
    tokens = ur_tokenizer("1,000 اور ۱٬۰۰۰")
    assert [token.text for token in tokens] == ["1,000", "اور", "۱٬۰۰۰"]
    assert tokens[0].like_num
    assert tokens[2].like_num


def test_ur_list_comma_is_not_numeric_grouping(ur_tokenizer):
    tokens = ur_tokenizer("1،2")
    assert [token.text for token in tokens] == ["1", "،", "2"]
    assert tokens[0].like_num
    assert not tokens[1].like_num
    assert tokens[2].like_num

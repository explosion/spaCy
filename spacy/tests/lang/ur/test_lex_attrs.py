import pytest

from spacy.lang.ur.lex_attrs import like_num


@pytest.mark.parametrize(
    "word",
    [
        "صفر",
        "ایک",
        "اٹھارہ",
        "چھبیس",
        "انچاس",
        "ساٹھ",
        "سو",
        "اٹهارا",
        "ساثھ",
        "ہزار",
        "لاکھ",
        "کروڑ",
        "18",
        "۱۸",
        "١٨",
        "1,000",
        "3.14",
        "۱٫۵",
        "-17",
        "+۲",
        "3/4",
        "پہلا",
        "اٹھارواں",
        "بیسواں",
    ],
)
def test_ur_lex_attrs_like_num_true(word):
    assert like_num(word)


@pytest.mark.parametrize(
    "word",
    [
        "کتاب",
        "اور",
        "اسلام",
        "آباد",
        "سونا",
        "واں",
        "سال",
        "ڈاکٹر",
        "خان",
        "کتابواں",
        "سالواں",
        "واں",
        "ویں",
        "1،2",
        "50%",
        "۵۰٪",
    ],
)
def test_ur_lex_attrs_like_num_false(word):
    assert not like_num(word)


def test_ur_like_num_digit_scripts_use_str_isdigit():
    """ASCII, Arabic-Indic, and Eastern Arabic-Indic digits are True because
    Python str.isdigit already accepts them, as in spacy.lang.lex_attrs.like_num.
    """
    assert "18".isdigit() and like_num("18")
    assert "۱۸".isdigit() and like_num("۱۸")
    assert "١٨".isdigit() and like_num("١٨")


def test_ur_like_num_separators_are_script_specific():
    assert like_num("1,000")
    assert like_num("1,2")  # inherited ASCII grouping heuristic, not a list parser
    assert like_num("۳٫۱۴")
    assert like_num("۱٬۰۰۰")
    assert like_num("3.14")
    assert like_num("-17")
    assert like_num("۳/۴")
    assert not like_num("1،2")
    assert not like_num("۱،۲")


@pytest.mark.parametrize(
    "text,expected",
    [
        ("صفر", True),
        ("اٹھارہ", True),
        ("چھبیس", True),
        ("انچاس", True),
        ("ساٹھ", True),
        ("ہزار", True),
        ("لاکھ", True),
        ("کروڑ", True),
        ("کتاب", False),
    ],
)
def test_ur_token_like_num(ur_tokenizer, text, expected):
    tokens = ur_tokenizer(text)
    assert tokens[0].like_num is expected

import unicodedata

from ...attrs import IS_CURRENCY, LIKE_NUM
from .punctuation import LIST_CURRENCY

_num_words = [
    "nol",
    "satu",
    "dua",
    "tiga",
    "empat",
    "lima",
    "enam",
    "tujuh",
    "delapan",
    "sembilan",
    "sepuluh",
    "sebelas",
    "belas",
    "puluh",
    "ratus",
    "ribu",
    "juta",
    "miliar",
    "biliun",
    "triliun",
    "kuadriliun",
    "kuintiliun",
    "sekstiliun",
    "septiliun",
    "oktiliun",
    "noniliun",
    "desiliun",
]


def like_num(text):
    if text.startswith(("+", "-", "±", "~")):
        text = text[1:]
    text = text.replace(",", "").replace(".", "")
    if text.isdigit():
        return True
    if text.count("/") == 1:
        num, denom = text.split("/")
        if num.isdigit() and denom.isdigit():
            return True
    if text.lower() in _num_words:
        return True
    if text.count("-") == 1:
        _, num = text.split("-")
        if num.isdigit() or num in _num_words:
            return True
    return False


def is_currency(text):
    if text in LIST_CURRENCY:
        return True

    for char in text:
        if unicodedata.category(char) != "Sc":
            return False
    return True


LEX_ATTRS = {IS_CURRENCY: is_currency, LIKE_NUM: like_num}

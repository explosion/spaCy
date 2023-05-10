from ...attrs import LIKE_NUM, NORM, PREFIX, SUFFIX


_num_words = [
    "нула",
    "један",
    "два",
    "три",
    "четири",
    "пет",
    "шест",
    "седам",
    "осам",
    "девет",
    "десет",
    "једанаест",
    "дванаест",
    "тринаест",
    "четрнаест",
    "петнаест",
    "шеснаест",
    "седамнаест",
    "осамнаест",
    "деветнаест",
    "двадесет",
    "тридесет",
    "четрдесет",
    "педесет",
    "шездесет",
    "седамдесет",
    "осамдесет",
    "деведесет",
    "сто",
    "двеста",
    "триста",
    "четиристо",
    "петсто",
    "шестсто",
    "седамсто",
    "осамсто",
    "деветсто",
    "хиљаду",
    "милион",
    "милијарду",
    "трилион",
    "квадрилион",
    "квинтилион",
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
    return False


def _cyr_to_latin_norm(text):
    # fmt: off
    # source: https://github.com/opendatakosovo/cyrillic-transliteration/blob/v1.1.1/cyrtranslit/mapping.py
    SR_CYR_TO_LAT_DICT = {
        u'А': u'A', u'а': u'a',
        u'Б': u'B', u'б': u'b',
        u'В': u'V', u'в': u'v',
        u'Г': u'G', u'г': u'g',
        u'Д': u'D', u'д': u'd',
        u'Ђ': u'Đ', u'ђ': u'đ',
        u'Е': u'E', u'е': u'e',
        u'Ж': u'Ž', u'ж': u'ž',
        u'З': u'Z', u'з': u'z',
        u'И': u'I', u'и': u'i',
        u'Ј': u'J', u'ј': u'j',
        u'К': u'K', u'к': u'k',
        u'Л': u'L', u'л': u'l',
        u'Љ': u'Lj', u'љ': u'lj',
        u'М': u'M', u'м': u'm',
        u'Н': u'N', u'н': u'n',
        u'Њ': u'Nj', u'њ': u'nj',
        u'О': u'O', u'о': u'o',
        u'П': u'P', u'п': u'p',
        u'Р': u'R', u'р': u'r',
        u'С': u'S', u'с': u's',
        u'Т': u'T', u'т': u't',
        u'Ћ': u'Ć', u'ћ': u'ć',
        u'У': u'U', u'у': u'u',
        u'Ф': u'F', u'ф': u'f',
        u'Х': u'H', u'х': u'h',
        u'Ц': u'C', u'ц': u'c',
        u'Ч': u'Č', u'ч': u'č',
        u'Џ': u'Dž', u'џ': u'dž',
        u'Ш': u'Š', u'ш': u'š',
    }
    # fmt: on
    return "".join(SR_CYR_TO_LAT_DICT.get(c, c) for c in text)


def norm(text):
    return _cyr_to_latin_norm(text).lower()


def prefix(text):
    return _cyr_to_latin_norm(text)[0]


def suffix(text):
    return _cyr_to_latin_norm(text)[-3:]


LEX_ATTRS = {LIKE_NUM: like_num, NORM: norm, PREFIX: prefix, SUFFIX: suffix}

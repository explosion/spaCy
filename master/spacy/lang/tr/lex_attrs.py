from ...attrs import LIKE_NUM


# Thirteen, fifteen etc. are written separate: on üç

_num_words = [
    "bir",
    "iki",
    "üç",
    "dört",
    "beş",
    "altı",
    "yedi",
    "sekiz",
    "dokuz",
    "on",
    "yirmi",
    "otuz",
    "kırk",
    "elli",
    "altmış",
    "yetmiş",
    "seksen",
    "doksan",
    "yüz",
    "bin",
    "milyon",
    "milyar",
    "trilyon",
    "katrilyon",
    "kentilyon",
]


_ordinal_words = [
    "birinci",
    "ikinci",
    "üçüncü",
    "dördüncü",
    "beşinci",
    "altıncı",
    "yedinci",
    "sekizinci",
    "dokuzuncu",
    "onuncu",
    "yirminci",
    "otuzuncu",
    "kırkıncı",
    "ellinci",
    "altmışıncı",
    "yetmişinci",
    "sekseninci",
    "doksanıncı",
    "yüzüncü",
    "bininci",
    "milyonuncu",
    "milyarıncı",
    "trilyonuncu",
    "katrilyonuncu",
    "kentilyonuncu",
]

_ordinal_endings = ("inci", "ıncı", "nci", "ncı", "uncu", "üncü")


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
    text_lower = text.lower()
    # Check cardinal number
    if text_lower in _num_words:
        return True
    # Check ordinal number
    if text_lower in _ordinal_words:
        return True
    if text_lower.endswith(_ordinal_endings):
        if text_lower[:-3].isdigit() or text_lower[:-4].isdigit():
            return True
    return False


LEX_ATTRS = {LIKE_NUM: like_num}

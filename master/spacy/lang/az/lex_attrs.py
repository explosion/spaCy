from ...attrs import LIKE_NUM


# Eleven, twelve etc. are written separate: on bir, on iki

_num_words = [
    "bir",
    "iki",
    "üç",
    "dörd",
    "beş",
    "altı",
    "yeddi",
    "səkkiz",
    "doqquz",
    "on",
    "iyirmi",
    "otuz",
    "qırx",
    "əlli",
    "altmış",
    "yetmiş",
    "səksən",
    "doxsan",
    "yüz",
    "min",
    "milyon",
    "milyard",
    "trilyon",
    "kvadrilyon",
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
    "səkkizinci",
    "doqquzuncu",
    "onuncu",
    "iyirminci",
    "otuzuncu",
    "qırxıncı",
    "əllinci",
    "altmışıncı",
    "yetmişinci",
    "səksəninci",
    "doxsanıncı",
    "yüzüncü",
    "mininci",
    "milyonuncu",
    "milyardıncı",
    "trilyonuncu",
    "kvadrilyonuncu",
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

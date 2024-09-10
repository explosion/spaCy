from ...attrs import LIKE_NUM

_num_words = [
    "sifir",
    "yek",
    "du",
    "sê",
    "çar",
    "pênc",
    "şeş",
    "heft",
    "heşt",
    "neh",
    "deh",
    "yazde",
    "dazde",
    "sêzde",
    "çarde",
    "pazde",
    "şazde",
    "hevde",
    "hejde",
    "nozde",
    "bîst",
    "sî",
    "çil",
    "pêncî",
    "şêst",
    "heftê",
    "heştê",
    "nod",
    "sed",
    "hezar",
    "milyon",
    "milyar",
]

_ordinal_words = [
    "yekem",
    "yekemîn",
    "duyem",
    "duyemîn",
    "sêyem",
    "sêyemîn",
    "çarem",
    "çaremîn",
    "pêncem",
    "pêncemîn",
    "şeşem",
    "şeşemîn",
    "heftem",
    "heftemîn",
    "heştem",
    "heştemîn",
    "nehem",
    "nehemîn",
    "dehem",
    "dehemîn",
    "yazdehem",
    "yazdehemîn",
    "dazdehem",
    "dazdehemîn",
    "sêzdehem",
    "sêzdehemîn",
    "çardehem",
    "çardehemîn",
    "pazdehem",
    "pazdehemîn",
    "şanzdehem",
    "şanzdehemîn",
    "hevdehem",
    "hevdehemîn",
    "hejdehem",
    "hejdehemîn",
    "nozdehem",
    "nozdehemîn",
    "bîstem",
    "bîstemîn",
    "sîyem",
    "sîyemîn",
    "çilem",
    "çilemîn",
    "pêncîyem",
    "pênciyemîn",
    "şêstem",
    "şêstemîn",
    "heftêyem",
    "heftêyemîn",
    "heştêyem",
    "heştêyemîn",
    "notem",
    "notemîn",
    "sedem",
    "sedemîn",
    "hezarem",
    "hezaremîn",
    "milyonem",
    "milyonemîn",
    "milyarem",
    "milyaremîn",
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
    text_lower = text.lower()
    if text_lower in _num_words:
        return True

    # Check ordinal number
    if text_lower in _ordinal_words:
        return True

    if is_digit(text_lower):
        return True

    return False


def is_digit(text):
    endings = ("em", "yem", "emîn", "yemîn")
    for ending in endings:
        to = len(ending)
        if text.endswith(ending) and text[:-to].isdigit():
            return True

    return False


LEX_ATTRS = {LIKE_NUM: like_num}

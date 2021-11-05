from ...attrs import LIKE_NUM

_num_words = [
    "ዜሮ",
    "ሓደ",
    "ክልተ",
    "ሰለስተ",
    "ኣርባዕተ",
    "ሓሙሽተ",
    "ሽድሽተ",
    "ሸውዓተ",
    "ሽሞንተ",
    "ትሽዓተ",
    "ዓሰርተ",
    "ዕስራ",
    "ሰላሳ",
    "ኣርብዓ",
    "ሓምሳ",
    "ሱሳ",
    "ሰብዓ",
    "ሰማንያ",
    "ቴስዓ",
    "ሚእቲ",
    "ሺሕ",
    "ሚልዮን",
    "ቢልዮን",
    "ትሪልዮን",
    "ኳድሪልዮን",
    "ጋዚልዮን",
    "ባዚልዮን",
]

# Tigrinya ordinals above 10 are the same as _num_words but start with "መበል "
_ordinal_words = [
    "ቀዳማይ",
    "ካልኣይ",
    "ሳልሳይ",
    "ራብዓይ",
    "ሓምሻይ",
    "ሻድሻይ",
    "ሻውዓይ",
    "ሻምናይ",
    "ታሽዓይ",
    "ዓስራይ",
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
    if text_lower.endswith("ይ"):
        if text_lower[:-2].isdigit():
            return True

    return False


LEX_ATTRS = {LIKE_NUM: like_num}

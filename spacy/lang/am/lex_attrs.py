from ...attrs import LIKE_NUM

_num_words = [
    "ዜሮ",
    "አንድ",
    "ሁለት",
    "ሶስት",
    "አራት",
    "አምስት",
    "ስድስት",
    "ሰባት",
    "ስምት",
    "ዘጠኝ",
    "አስር",
    "አስራ አንድ",
    "አስራ ሁለት",
    "አስራ ሶስት",
    "አስራ አራት",
    "አስራ አምስት",
    "አስራ ስድስት",
    "አስራ ሰባት",
    "አስራ ስምንት",
    "አስራ ዘጠኝ",
    "ሃያ",
    "ሰላሳ",
    "አርባ",
    "ሃምሳ",
    "ስልሳ",
    "ሰባ",
    "ሰማንያ",
    "ዘጠና",
    "መቶ",
    "ሺህ",
    "ሚሊዮን",
    "ቢሊዮን",
    "ትሪሊዮን",
    "ኳድሪሊዮን",
    "ገጅሊዮን",
    "ባዝሊዮን",
]

_ordinal_words = [
    "አንደኛ",
    "ሁለተኛ",
    "ሶስተኛ",
    "አራተኛ",
    "አምስተኛ",
    "ስድስተኛ",
    "ሰባተኛ",
    "ስምንተኛ",
    "ዘጠነኛ",
    "አስረኛ",
    "አስራ አንደኛ",
    "አስራ ሁለተኛ",
    "አስራ ሶስተኛ",
    "አስራ አራተኛ",
    "አስራ አምስተኛ",
    "አስራ ስድስተኛ",
    "አስራ ሰባተኛ",
    "አስራ ስምንተኛ",
    "አስራ ዘጠነኛ",
    "ሃያኛ",
    "ሰላሳኛ" "አርባኛ",
    "አምሳኛ",
    "ስድሳኛ",
    "ሰባኛ",
    "ሰማንያኛ",
    "ዘጠናኛ",
    "መቶኛ",
    "ሺኛ",
    "ሚሊዮንኛ",
    "ቢሊዮንኛ",
    "ትሪሊዮንኛ",
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
    if text_lower.endswith("ኛ"):
        if text_lower[:-2].isdigit():
            return True

    return False


LEX_ATTRS = {LIKE_NUM: like_num}

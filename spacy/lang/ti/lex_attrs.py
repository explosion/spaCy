from ...attrs import LIKE_NUM

_num_words = [
    "ዜሮ",
    "ሐደ",
    "ክልተ",
    "ሰለስተ",
    "ኣርባዕተ",
    "ሓሙሽተ",
    "ሽድሽተ",
    "ሸውዓተ",
    "ሽሞንተ",
    "ትሽዓተ",
    "ኣሰርተ",
    "ኣሰርተ ሐደ",
    "ኣሰርተ ክልተ",
    "ኣሰርተ ሰለስተ",
    "ኣሰርተ ኣርባዕተ",
    "ኣሰርተ ሓሙሽተ",
    "ኣሰርተ ሽድሽተ",
    "ኣሰርተ ሸውዓተ",
    "ኣሰርተ ሽሞንተ",
    "ኣሰርተ ትሽዓተ",
    "ዕስራ",
    "ሰላሳ",
    "ኣርብዓ",
    "ሃምሳ",
    "ስልሳ",
    "ሰብዓ",
    "ሰማንያ",
    "ተስዓ",
    "ሚእቲ",
    "ሺሕ",
    "ሚልዮን",
    "ቢልዮን",
    "ትሪልዮን",
    "ኳድሪልዮን",
    "ገጅልዮን",
    "ባዝልዮን",
]

_ordinal_words = [
    "ቀዳማይ",
    "ካልኣይ",
    "ሳልሳይ",
    "ራብኣይ",
    "ሓምሻይ",
    "ሻድሻይ",
    "ሻውዓይ",
    "ሻምናይ",
    "ዘጠነኛ",
    "አስረኛ",
    "ኣሰርተ አንደኛ",
    "ኣሰርተ ሁለተኛ",
    "ኣሰርተ ሶስተኛ",
    "ኣሰርተ አራተኛ",
    "ኣሰርተ አምስተኛ",
    "ኣሰርተ ስድስተኛ",
    "ኣሰርተ ሰባተኛ",
    "ኣሰርተ ስምንተኛ",
    "ኣሰርተ ዘጠነኛ",
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

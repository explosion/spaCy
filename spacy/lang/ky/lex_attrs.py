from ...attrs import LIKE_NUM

_num_words = [
    "нөл",
    "ноль",
    "бир",
    "эки",
    "үч",
    "төрт",
    "беш",
    "алты",
    "жети",
    "сегиз",
    "тогуз",
    "он",
    "жыйырма",
    "отуз",
    "кырк",
    "элүү",
    "алтымыш",
    "жетмиш",
    "сексен",
    "токсон",
    "жүз",
    "миң",
    "миллион",
    "миллиард",
    "триллион",
    "триллиард",
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
    if text in _num_words:
        return True
    return False


LEX_ATTRS = {LIKE_NUM: like_num}

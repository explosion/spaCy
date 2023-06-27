from ...attrs import LIKE_NUM

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


LEX_ATTRS = {LIKE_NUM: like_num}

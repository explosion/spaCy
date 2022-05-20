from ...attrs import LIKE_NUM

_num_words = [
    "nul",
    "jaden",
    "jadna",
    "jadno",
    "dwa",
    "dwě",
    "tśi",
    "tśo",
    "styri",
    "styrjo",
    "pěś",
    "pěśo",
    "šesć",
    "šesćo",
    "sedym",
    "sedymjo",
    "wósym",
    "wósymjo",
    "źewjeś",
    "źewjeśo",
    "źaseś",
    "źaseśo",
    "jadnassćo",
    "dwanassćo",
    "tśinasćo",
    "styrnasćo",
    "pěśnasćo",
    "šesnasćo",
    "sedymnasćo",
    "wósymnasćo",
    "źewjeśnasćo",
    "dwanasćo",
    "dwaźasća",
    "tśiźasća",
    "styrźasća",
    "pěśźaset",
    "šesćźaset",
    "sedymźaset",
    "wósymźaset",
    "źewjeśźaset",
    "sto",
    "tysac",
    "milion",
    "miliarda",
    "bilion",
    "biliarda",
    "trilion",
    "triliarda",
]

_ordinal_words = [
    "prědny",
    "prědna",
    "prědne",
    "drugi",
    "druga",
    "druge",
    "tśeśi",
    "tśeśa",
    "tśeśe",
    "stwórty",
    "stwórta",
    "stwórte",
    "pêty",
    "pěta",
    "pête",
    "šesty",
    "šesta",
    "šeste",
    "sedymy",
    "sedyma",
    "sedyme",
    "wósymy",
    "wósyma",
    "wósyme",
    "źewjety",
    "źewjeta",
    "źewjete",
    "źasety",
    "źaseta",
    "źasete",
    "jadnasty",
    "jadnasta",
    "jadnaste",
    "dwanasty",
    "dwanasta",
    "dwanaste",
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
    return False


LEX_ATTRS = {LIKE_NUM: like_num}

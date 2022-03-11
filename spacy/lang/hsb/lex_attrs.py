from ...attrs import LIKE_NUM

_num_words = [
    "nul",
    "jedyn",
    "jedna",
    "jedne",
    "dwaj",
    "dwě",
    "tři",
    "třo",
    "štyri",
    "štyrjo",
    "pjeć",
    "šěsć",
    "sydom",
    "wosom",
    "dźewjeć",
    "dźesać",
    "jědnaće",
    "dwanaće",
    "třinaće",
    "štyrnaće",
    "pjatnaće",
    "šěsnaće",
    "sydomnaće",
    "wosomnaće",
    "dźewjatnaće",
    "dwaceći",
    "třiceći",
    "štyrceći",
    "pjećdźesat",
    "šěsćdźesat",
    "sydomdźesat",
    "wosomdźesat",
    "dźewjećdźesat",
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
    "prěni",
    "prěnja",
    "prěnje",
    "druhi",
    "druha",
    "druhe",
    "třeći",
    "třeća",
    "třeće",
    "štwórty",
    "štwórta",
    "štwórte",
    "pjaty",
    "pjata",
    "pjate",
    "šěsty",
    "šěsta",
    "šěste",
    "sydmy",
    "sydma",
    "sydme",
    "wosmy",
    "wosma",
    "wosme",
    "dźewjaty",
    "dźewjata",
    "dźewjate",
    "dźesaty",
    "dźesata",
    "dźesate",
    "jědnaty",
    "jědnata",
    "jědnate",
    "dwanaty",
    "dwanata",
    "dwanate",
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

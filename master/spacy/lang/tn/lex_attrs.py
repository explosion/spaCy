from ...attrs import LIKE_NUM

_num_words = [
    "lefela",
    "nngwe",
    "pedi",
    "tharo",
    "nne",
    "tlhano",
    "thataro",
    "supa",
    "robedi",
    "robongwe",
    "lesome",
    "lesomenngwe",
    "lesomepedi",
    "sometharo",
    "somenne",
    "sometlhano",
    "somethataro",
    "somesupa",
    "somerobedi",
    "somerobongwe",
    "someamabedi",
    "someamararo",
    "someamane",
    "someamatlhano",
    "someamarataro",
    "someamasupa",
    "someamarobedi",
    "someamarobongwe",
    "lekgolo",
    "sekete",
    "milione",
    "bilione",
    "terilione",
    "kwatirilione",
    "gajillione",
    "bazillione",
]


_ordinal_words = [
    "ntlha",
    "bobedi",
    "boraro",
    "bone",
    "botlhano",
    "borataro",
    "bosupa",
    "borobedi ",
    "borobongwe",
    "bolesome",
    "bolesomengwe",
    "bolesomepedi",
    "bolesometharo",
    "bolesomenne",
    "bolesometlhano",
    "bolesomethataro",
    "bolesomesupa",
    "bolesomerobedi",
    "bolesomerobongwe",
    "somamabedi",
    "someamararo",
    "someamane",
    "someamatlhano",
    "someamarataro",
    "someamasupa",
    "someamarobedi",
    "someamarobongwe",
    "lekgolo",
    "sekete",
    "milione",
    "bilione",
    "terilione",
    "kwatirilione",
    "gajillione",
    "bazillione",
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

    # CHeck ordinal number
    if text_lower in _ordinal_words:
        return True
    if text_lower.endswith("th"):
        if text_lower[:-2].isdigit():
            return True

    return False


LEX_ATTRS = {LIKE_NUM: like_num}

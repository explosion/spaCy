from ...attrs import LIKE_NUM


_num_words = set(
    """
zero unu doi două trei patru cinci șase șapte opt nouă zece
unsprezece doisprezece douăsprezece treisprezece patrusprezece cincisprezece șaisprezece șaptesprezece optsprezece nouăsprezece
douăzeci treizeci patruzeci cincizeci șaizeci șaptezeci optzeci nouăzeci
sută mie milion miliard bilion trilion cvadrilion catralion cvintilion sextilion septilion enșpemii
""".split()
)

_ordinal_words = set(
    """
primul doilea treilea patrulea cincilea șaselea șaptelea optulea nouălea zecelea
prima doua treia patra cincia șasea șaptea opta noua zecea
unsprezecelea doisprezecelea treisprezecelea patrusprezecelea cincisprezecelea șaisprezecelea șaptesprezecelea optsprezecelea nouăsprezecelea
unsprezecea douăsprezecea treisprezecea patrusprezecea cincisprezecea șaisprezecea șaptesprezecea optsprezecea nouăsprezecea
douăzecilea treizecilea patruzecilea cincizecilea șaizecilea șaptezecilea optzecilea nouăzecilea sutălea
douăzecea treizecea patruzecea cincizecea șaizecea șaptezecea optzecea nouăzecea suta
miilea mielea mia milionulea milioana miliardulea miliardelea miliarda enșpemia
""".split()
)


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
    if text.lower() in _ordinal_words:
        return True
    return False


LEX_ATTRS = {LIKE_NUM: like_num}

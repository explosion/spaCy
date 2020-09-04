from ...attrs import LIKE_NUM


_num_words = set(
    """
zero un deux trois quatre cinq six sept huit neuf dix
onze douze treize quatorze quinze seize dix-sept dix-huit dix-neuf
vingt trente quarante cinquante soixante soixante-dix septante quatre-vingt huitante quatre-vingt-dix nonante
cent mille mil million milliard billion quadrillion quintillion
sextillion septillion octillion nonillion decillion
""".split()
)

_ordinal_words = set(
    """
premier deuxième second troisième quatrième cinquième sixième septième huitième neuvième dixième
onzième douzième treizième quatorzième quinzième seizième dix-septième dix-huitième dix-neuvième
vingtième trentième quarantième cinquantième soixantième soixante-dixième septantième quatre-vingtième huitantième quatre-vingt-dixième nonantième
centième millième millionnième milliardième billionnième quadrillionnième quintillionnième
sextillionnième septillionnième octillionnième nonillionnième decillionnième
""".split()
)


def like_num(text):
    # Might require more work?
    # See this discussion: https://github.com/explosion/spaCy/pull/1161
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

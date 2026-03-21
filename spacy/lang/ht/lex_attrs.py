from ...attrs import LIKE_NUM, NORM

# Cardinal numbers in Creole
_num_words = set(
    """
zewo youn en de twa kat senk sis sèt uit nèf dis
onz douz trèz katoz kenz sèz disèt dizwit diznèf
vent trant karant sinkant swasant swasann-dis
san mil milyon milya
""".split()
)

# Ordinal numbers in Creole (some are French-influenced, some simplified)
_ordinal_words = set(
    """
premye dezyèm twazyèm katryèm senkyèm sizyèm sètvyèm uitvyèm nèvyèm dizyèm
onzèm douzyèm trèzyèm katozyèm kenzèm sèzyèm disetyèm dizwityèm diznèvyèm
ventyèm trantyèm karantyèm sinkantyèm swasantyèm
swasann-disyèm santyèm milyèm milyonnyèm milyadyèm
""".split()
)

NORM_MAP = {
    "'m": "mwen",
    "'w": "ou",
    "'l": "li",
    "'n": "nou",
    "'y": "yo",
    "’m": "mwen",
    "’w": "ou",
    "’l": "li",
    "’n": "nou",
    "’y": "yo",
    "m": "mwen",
    "n": "nou",
    "l": "li",
    "y": "yo",
    "w": "ou",
    "t": "te",
    "k": "ki",
    "p": "pa",
    "M": "Mwen",
    "N": "Nou",
    "L": "Li",
    "Y": "Yo",
    "W": "Ou",
    "T": "Te",
    "K": "Ki",
    "P": "Pa",
}


def like_num(text):
    text = text.strip().lower()
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
    if text in _ordinal_words:
        return True
    # Handle things like "3yèm", "10yèm", "25yèm", etc.
    if text.endswith("yèm") and text[:-3].isdigit():
        return True
    return False


def norm_custom(text):
    return NORM_MAP.get(text, text.lower())


LEX_ATTRS = {
    LIKE_NUM: like_num,
    NORM: norm_custom,
}

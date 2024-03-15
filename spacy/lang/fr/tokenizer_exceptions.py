import re

_hyphen = "-–—"
_apostrophe = "'`´’"

# fmt: off
_suffix_inversion = r"|".join([
    "je", "tu", "on", "il", "elle", "iel",
    "nous", "vous", "elles", "ils", "iels",
    # écoutons-les
    "moi", "toi", "lui", "leur",
    "eux",
    fr"en(?![{_hyphen}])", "y",
    # écoutons-les
    fr"la(?![{_hyphen}])", fr"le(?![{_hyphen}])", fr"les(?![{_hyphen}])",
    # a-t-il, pourra-t'on, dis-m'en plus
    fr"t[{_hyphen}]??[{_apostrophe}]?", fr"m[{_apostrophe}]?",
    "là", "ici",
])
_prefix_elision = r"|".join([
    "n", "s", "c", "d", "j", "m", "t", "l", "qu",
    # i exclude "quelqu'un"/"quelqu'un" because it's one token (and not quelque + un, which lack the idea of 'one person').
    fr"quelqu(?![{_apostrophe}]un[ex]*\b)",  # quelque
    "jusqu", "presqu", "lorsqu", "puisqu", "quoiqu",
])
# fmt: on

_elision = rf"(?:\b(?:{_prefix_elision})[{_apostrophe}])"
_inversion = (
    rf"(?:(?<=[^\W\d])[{_hyphen}]\b(?:{_suffix_inversion})\b)"
)

TOKEN_MATCH = re.compile(
    r"(?iu)" + r"|".join([_inversion, _elision])
)
# _abbrevs = ["ste?", "mme", "mr?", "mlle", "dr", "etc", "cf"]

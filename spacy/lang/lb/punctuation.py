from ..char_classes import ALPHA, ALPHA_LOWER, ALPHA_UPPER, LIST_ELLIPSES, LIST_ICONS

ELISION = " ' ’ ".strip().replace(" ", "")

abbrev = ("d", "D")

_infixes = (
    LIST_ELLIPSES
    + LIST_ICONS
    + [
        r"(?<=^[{ab}][{el}])(?=[{a}])".format(ab=abbrev, a=ALPHA, el=ELISION),
        r"(?<=[{al}])\.(?=[{au}])".format(al=ALPHA_LOWER, au=ALPHA_UPPER),
        r"(?<=[{a}])[,!?](?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}])[:<>=](?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}])--(?=[{a}])".format(a=ALPHA),
        r"(?<=[0-9])-(?=[0-9])",
    ]
)

TOKENIZER_INFIXES = _infixes

from ..char_classes import (
    ALPHA,
    ALPHA_LOWER,
    ALPHA_UPPER,
    CONCAT_QUOTES,
    HYPHENS,
    LIST_ELLIPSES,
    LIST_ICONS,
)

_hyphens_no_dash = HYPHENS.replace("-", "").strip("|").replace("||", "")
_infixes = (
    LIST_ELLIPSES
    + LIST_ICONS
    + [
        r"(?<=[{al}])\.(?=[{au}])".format(al=ALPHA_LOWER, au=ALPHA_UPPER),
        r"(?<=[{a}])[,!?/()]+(?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}{q}])[:<>=](?=[{a}])".format(a=ALPHA, q=CONCAT_QUOTES),
        r"(?<=[{a}])--(?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}])([{q}\)\]\(\[])(?=[\-{a}])".format(a=ALPHA, q=CONCAT_QUOTES),
        r"(?<=[{a}])(?:{h})(?=[{a}])".format(a=ALPHA, h=_hyphens_no_dash),
        r"(?<=[0-9])-(?=[0-9])",
    ]
)

TOKENIZER_INFIXES = _infixes

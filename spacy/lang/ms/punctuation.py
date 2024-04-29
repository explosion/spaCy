from ..char_classes import ALPHA, _currency, _units, merge_chars, split_chars
from ..punctuation import TOKENIZER_INFIXES, TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES

_units = (
    _units + "s bit Gbps Mbps mbps Kbps kbps ƒ ppi px "
    "Hz kHz MHz GHz mAh "
    "ratus rb ribu ribuan "
    "juta jt jutaan mill?iar million bil[l]?iun bilyun billion "
)
_currency = _currency + r" USD RM MYR Rp IDR RMB SGD S\$"
_months = (
    "Januari Februari Mac April Mei Jun Julai Ogos September "
    "Oktober November Disember Januari Februari Mac Mei Jun "
    "Julai Ogos Oktober Disember Jan Feb Mac Jun Julai Ogos Sept "
    "Okt Nov Dis"
)


UNITS = merge_chars(_units)
CURRENCY = merge_chars(_currency)
HTML_PREFIX = r"<(b|strong|i|em|p|span|div|br)\s?/>|<a([^>]+)>"
HTML_SUFFIX = r"</(b|strong|i|em|p|span|div|a)>"
MONTHS = merge_chars(_months)
LIST_CURRENCY = split_chars(_currency)

_prefixes = list(TOKENIZER_PREFIXES)
_prefixes.remove("#")  # hashtag
_prefixes = _prefixes + LIST_CURRENCY + [HTML_PREFIX] + ["/", "—"]

_suffixes = (
    TOKENIZER_SUFFIXES
    + [r"\-[Nn]ya", "-[KkMm]u", "[—-]"]
    + [
        # disabled: variable width currency variable
        # r"(?<={c})(?:[0-9]+)".format(c=CURRENCY),
        r"(?<=[0-9])(?:{u})".format(u=UNITS),
        r"(?<=[0-9])%",
        # disabled: variable width HTML_SUFFIX variable
        # r"(?<=[0-9{a}]{h})(?:[\.,:-])".format(a=ALPHA, h=HTML_SUFFIX),
        r"(?<=[0-9{a}])(?:{h})".format(a=ALPHA, h=HTML_SUFFIX),
    ]
)

_infixes = TOKENIZER_INFIXES + [
    r"(?<=[0-9])[\\/](?=[0-9%-])",
    r"(?<=[0-9])%(?=[{a}0-9/])".format(a=ALPHA),
    # disabled: variable width units variable
    # r"(?<={u})[\/-](?=[0-9])".format(u=UNITS),
    # disabled: variable width months variable
    # r"(?<={m})[\/-](?=[0-9])".format(m=MONTHS),
    r'(?<=[0-9)][.,])"(?=[0-9])',
    r'(?<=[{a})][.,\'])["—](?=[{a}])'.format(a=ALPHA),
    r"(?<=[{a}])-(?=[0-9])".format(a=ALPHA),
    r"(?<=[0-9])-(?=[{a}])".format(a=ALPHA),
    r"(?<=[{a}])[\/-](?={c}|[{a}])".format(a=ALPHA, c=CURRENCY),
]

TOKENIZER_PREFIXES = _prefixes
TOKENIZER_SUFFIXES = _suffixes
TOKENIZER_INFIXES = _infixes

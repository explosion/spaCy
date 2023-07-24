from ..char_classes import (
    ALPHA,
    ALPHA_LOWER,
    ALPHA_UPPER,
    CONCAT_QUOTES,
    CURRENCY,
    HYPHENS,
    LIST_CURRENCY,
    LIST_ELLIPSES,
    LIST_ICONS,
    LIST_PUNCT,
    LIST_QUOTES,
    PUNCT,
    UNITS,
    merge_chars,
)
from ..punctuation import TOKENIZER_PREFIXES as BASE_TOKENIZER_PREFIXES

INCLUDE_SPECIAL = ["\\+", "\\/", "\\•", "\\¯", "\\=", "\\×"] + HYPHENS.split("|")

_prefixes = INCLUDE_SPECIAL + BASE_TOKENIZER_PREFIXES

_suffixes = (
    INCLUDE_SPECIAL
    + LIST_PUNCT
    + LIST_ELLIPSES
    + LIST_QUOTES
    + LIST_ICONS
    + [
        r"(?<=°[FfCcKk])\.",
        r"(?<=[0-9])(?:{c})".format(c=CURRENCY),
        r"(?<=[0-9])(?:{u})".format(u=UNITS),
        r"(?<=[{al}{e}{p}(?:{q})])\.".format(
            al=ALPHA_LOWER, e=r"%²\-\+", q=CONCAT_QUOTES, p=PUNCT
        ),
        r"(?<=[{au}][{au}])\.".format(au=ALPHA_UPPER),
        # split initials like J.K. Rowling
        r"(?<=[A-Z]\.)(?:[A-Z].)",
    ]
)

# a list of all suffixes following a hyphen that are shouldn't split (eg. BTC-jev)
# source: Obeliks tokenizer - https://github.com/clarinsi/obeliks/blob/master/obeliks/res/TokRulesPart1.txt
CONCAT_QUOTES = CONCAT_QUOTES.replace("'", "")
HYPHENS_PERMITTED = (
    "((a)|(evemu)|(evskega)|(i)|(jevega)|(jevska)|(jevskimi)|(jinemu)|(oma)|(ovim)|"
    "(ovski)|(e)|(evi)|(evskem)|(ih)|(jevem)|(jevske)|(jevsko)|(jini)|(ov)|(ovima)|"
    "(ovskih)|(em)|(evih)|(evskemu)|(ja)|(jevemu)|(jevskega)|(ji)|(jinih)|(ova)|"
    "(ovimi)|(ovskim)|(ema)|(evim)|(evski)|(je)|(jevi)|(jevskem)|(jih)|(jinim)|"
    "(ove)|(ovo)|(ovskima)|(ev)|(evima)|(evskih)|(jem)|(jevih)|(jevskemu)|(jin)|"
    "(jinima)|(ovega)|(ovska)|(ovskimi)|(eva)|(evimi)|(evskim)|(jema)|(jevim)|"
    "(jevski)|(jina)|(jinimi)|(ovem)|(ovske)|(ovsko)|(eve)|(evo)|(evskima)|(jev)|"
    "(jevima)|(jevskih)|(jine)|(jino)|(ovemu)|(ovskega)|(u)|(evega)|(evska)|"
    "(evskimi)|(jeva)|(jevimi)|(jevskim)|(jinega)|(ju)|(ovi)|(ovskem)|(evem)|"
    "(evske)|(evsko)|(jeve)|(jevo)|(jevskima)|(jinem)|(om)|(ovih)|(ovskemu)|"
    "(ovec)|(ovca)|(ovcu)|(ovcem)|(ovcev)|(ovcema)|(ovcih)|(ovci)|(ovce)|(ovcimi)|"
    "(evec)|(evca)|(evcu)|(evcem)|(evcev)|(evcema)|(evcih)|(evci)|(evce)|(evcimi)|"
    "(jevec)|(jevca)|(jevcu)|(jevcem)|(jevcev)|(jevcema)|(jevcih)|(jevci)|(jevce)|"
    "(jevcimi)|(ovka)|(ovke)|(ovki)|(ovko)|(ovk)|(ovkama)|(ovkah)|(ovkam)|(ovkami)|"
    "(evka)|(evke)|(evki)|(evko)|(evk)|(evkama)|(evkah)|(evkam)|(evkami)|(jevka)|"
    "(jevke)|(jevki)|(jevko)|(jevk)|(jevkama)|(jevkah)|(jevkam)|(jevkami)|(timi)|"
    "(im)|(ima)|(a)|(imi)|(e)|(o)|(ega)|(ti)|(em)|(tih)|(emu)|(tim)|(i)|(tima)|"
    "(ih)|(ta)|(te)|(to)|(tega)|(tem)|(temu))"
)

_infixes = (
    LIST_ELLIPSES
    + LIST_ICONS
    + [
        r"(?<=[0-9])[+\-\*^](?=[0-9-])",
        r"(?<=[{al}{q}])\.(?=[{au}{q}])".format(
            al=ALPHA_LOWER, au=ALPHA_UPPER, q=CONCAT_QUOTES
        ),
        r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
        r"(?<=[{a}0-9])(?:{h})(?!{hp}$)(?=[{a}])".format(
            a=ALPHA, h=HYPHENS, hp=HYPHENS_PERMITTED
        ),
        r"(?<=[{a}0-9])[:<>=/](?=[{a}])".format(a=ALPHA),
    ]
)


TOKENIZER_PREFIXES = _prefixes
TOKENIZER_SUFFIXES = _suffixes
TOKENIZER_INFIXES = _infixes

from ...symbols import ORTH, NORM
from ...util import update_exc
from ..tokenizer_exceptions import BASE_EXCEPTIONS


# Returns capitalized variants, all caps variants and with curly apostrophe
def _variants(orth, exc):
    yield orth, exc
    yield orth.capitalize(), [
        {ORTH: e[ORTH].capitalize() if i == 0 else e[ORTH], NORM: e.get(NORM, e[ORTH])}
        for i, e in enumerate(exc)
    ]
    yield orth.upper(), [
        {ORTH: e[ORTH].upper(), NORM: e.get(NORM, e[ORTH])} for e in exc
    ]
    if "'" in orth:
        yield from _variants(
            orth.replace("'", "’"),
            [
                {ORTH: e[ORTH].replace("'", "’"), NORM: e.get(NORM, e[ORTH])}
                for e in exc
            ],
        )


_exc = {}

# Compound prepositions

# Compounds with "inte" and "de" aren't split as they can be ambiguous
# Format: (compound form, isolated form, determiners it goes with)
_preps = [
    ("a-", "à", "oaie"),
    ("co-", "con", "oaie"),
    ("da-", "da", "oaie"),
    ("pe-", "pe", "oaie"),
    ("pi-", "pe", "a"),  # colloquialism
    ("de-", "de", "oaie"),  # incorrect, but occasionally seen
    ("ne-", "inte", "oaie"),  # incorrect, but occasionally seen
]
for prep_, prep, dets in _preps:
    for det in dets:
        for orth, exc in _variants(
            prep_ + det, [{ORTH: prep_, NORM: prep}, {ORTH: det}]
        ):
            _exc[orth] = exc

# Units

for u in "cfkCFK":
    _exc[f"°{u}"] = [{ORTH: f"°{u}"}]
    _exc[f"°{u}."] = [{ORTH: f"°{u}"}, {ORTH: "."}]

# Other exceptions

_other_exc = {
    "'n'": [{ORTH: "'n'", NORM: "unna"}],
    "‘n'": [{ORTH: "‘n'", NORM: "unna"}],
    "'n": [{ORTH: "'n", NORM: "un"}],
    "‘n": [{ORTH: "‘n", NORM: "un"}],
    "tou": [{ORTH: "t", NORM: "te"}, {ORTH: "ou", NORM: "ô"}],
}
for orth_, exc_ in _other_exc.items():
    for orth, exc in _variants(orth_, exc_):
        _exc[orth] = exc

TOKENIZER_EXCEPTIONS = update_exc(BASE_EXCEPTIONS, _exc)

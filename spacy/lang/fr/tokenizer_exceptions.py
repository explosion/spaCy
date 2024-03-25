from ...symbols import NORM, ORTH
from ...util import update_exc
from ..tokenizer_exceptions import BASE_EXCEPTIONS

_exc = {
    "St": [{ORTH: "St", NORM: "Saint"}],
    "Ste": [{ORTH: "Ste", NORM: "Sainte"}],
    "Mme": [{ORTH: "Mme", NORM: "Madame"}],
    "Mr": [{ORTH: "Mr", NORM: "Monsieur"}],
    "M.": [{ORTH: "M.", NORM: "Monsieur"}],
    "Mlle": [{ORTH: "Mlle", NORM: "Mademoiselle"}],
    "Dr": [{ORTH: "Dr", NORM: "Docteur"}],
    "Dresse": [{ORTH: "Dresse", NORM: "Doctoresse"}],
    "Drsse": [{ORTH: "Drsse", NORM: "Doctoresse"}],
    "etc": [{ORTH: "etc", NORM: "etcaetera"}],
}

TOKENIZER_EXCEPTIONS = update_exc(BASE_EXCEPTIONS, _exc)

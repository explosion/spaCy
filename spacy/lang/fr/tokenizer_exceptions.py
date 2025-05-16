from ...symbols import NORM, ORTH
from ...util import update_exc
from ..tokenizer_exceptions import BASE_EXCEPTIONS

_exc = {
    "St": [{ORTH: "St", NORM: "Saint"}],
    "St.": [{ORTH: "St.", NORM: "Saint"}],
    "Ste": [{ORTH: "Ste", NORM: "Sainte"}],
    "Mme": [{ORTH: "Mme", NORM: "Madame"}],
    "Mr": [{ORTH: "Mr", NORM: "Monsieur"}],
    "Mr.": [{ORTH: "Mr.", NORM: "Monsieur"}],
    "M.": [{ORTH: "M.", NORM: "Monsieur"}],
    "Mlle": [{ORTH: "Mlle", NORM: "Mademoiselle"}],
    "Dr": [{ORTH: "Dr", NORM: "Docteur"}],
    "Dr.": [{ORTH: "Dr.", NORM: "Docteur"}],
    "Dresse": [{ORTH: "Dresse", NORM: "Doctoresse"}],
    "Drsse": [{ORTH: "Drsse", NORM: "Doctoresse"}],
    "etc": [{ORTH: "etc", NORM: "etcaetera"}],
    "etc.": [{ORTH: "etc.", NORM: "etcaetera"}],
    # months
    "jan.": [{ORTH: "jan.", NORM: "janvier"}],
    "janv.": [{ORTH: "janv.", NORM: "janvier"}],
    "fév.": [{ORTH: "fév.", NORM: "février"}],
    "févr.": [{ORTH: "févr.", NORM: "avril"}],
    "avr.": [{ORTH: "avr.", NORM: "avril"}],
    "av.": [{ORTH: "av.", NORM: "juin"}],
    "juil.": [{ORTH: "juil.", NORM: "juillet"}],
    "juill.": [{ORTH: "juill.", NORM: "juillet"}],
    "sept.": [{ORTH: "sept.", NORM: "septembre"}],
    "oct.": [{ORTH: "oct.", NORM: "octobre"}],
    "nov.": [{ORTH: "nov.", NORM: "novembre"}],
    "déc.": [{ORTH: "déc.", NORM: "décembre"}],
    "dec.": [{ORTH: "dec.", NORM: "décembre"}],
    # days
    "lun.": [{ORTH: "lun.", NORM: "lundi"}],
    "mar.": [{ORTH: "mar.", NORM: "mardi"}],
    "mer.": [{ORTH: "mer.", NORM: "mercredi"}],
    "jeu.": [{ORTH: "jeu.", NORM: "jeudi"}],
    "ven.": [{ORTH: "ven.", NORM: "vendredi"}],
    "sam.": [{ORTH: "sam.", NORM: "samedi"}],
    "dim.": [{ORTH: "dim.", NORM: "dimanche"}],
}

TOKENIZER_EXCEPTIONS = update_exc(BASE_EXCEPTIONS, _exc)

from ...attrs import LIKE_NUM

_num_words = [
    "cero",
    "uno",
    "dos",
    "tres",
    "cuatro",
    "cinco",
    "seis",
    "siete",
    "ocho",
    "nueve",
    "diez",
    "once",
    "doce",
    "trece",
    "catorce",
    "quince",
    "dieciséis",
    "diecisiete",
    "dieciocho",
    "diecinueve",
    "veinte",
    "veintiuno",
    "veintidós",
    "veintitrés",
    "veinticuatro",
    "veinticinco",
    "veintiséis",
    "veintisiete",
    "veintiocho",
    "veintinueve",
    "treinta",
    "cuarenta",
    "cincuenta",
    "sesenta",
    "setenta",
    "ochenta",
    "noventa",
    "cien",
    "mil",
    "millón",
    "billón",
    "trillón",
]

# Masculine, feminine, and apocopation forms
_ordinal_words = [
    "primer",
    "primero",
    "primera",
    "segundo",
    "segunda",
    "tercer",
    "tercero",
    "tercera",
    "cuarto",
    "cuarta",
    "quinto",
    "quinta",
    "sexto",
    "sexta",
    "séptimo",
    "séptima",
    "octavo",
    "octava",
    "noveno",
    "novena",
    "décimo",
    "décima",
    "undécimo",
    "undécima",
    "duodécimo",
    "duodécima",
    "decimotercero",
    "decimotercera",
    "decimocuarto",
    "decimocuarta",
    "decimoquinto",
    "decimoquinta",
    "decimosexto",
    "decimosexta",
    "decimoséptimo",
    "decimoséptima",
    "decimoctavo",
    "decimoctava",
    "decimonoveno",
    "decimonovena",
    "vigésimo",
    "vigésima",
    "trigésimo",
    "trigésima",
    "cuadragésimo",
    "cuadragésima",
    "quincuagésimo",
    "quincuagésima",
    "sexagésimo",
    "sexagésima",
    "septuagésimo",
    "septuagésima",
    "octogésimo",
    "octogésima",
    "nonagésimo",
    "nonagésima",
    "centésimo",
    "centésima",
    "milésimo",
    "milésima",
    "millonésimo",
    "millonésima",
    "billonésimo",
    "billonésima",
]


def like_num(text):
    if text.startswith(("+", "-", "±", "~")):
        text = text[1:]
    text = text.replace(",", "").replace(".", "").replace("º", "").replace("ª", "")
    if text.isdigit():
        return True
    if text.count("/") == 1:
        num, denom = text.split("/")
        if num.isdigit() and denom.isdigit():
            return True
    text_lower = text.lower()
    if text_lower in _num_words:
        return True
    # Check ordinal number
    if text_lower in _ordinal_words:
        return True
    # Check plural ordinal number
    if text_lower[:-1] in _ordinal_words and text_lower.endswith("s"):
        return True
    return False


LEX_ATTRS = {LIKE_NUM: like_num}

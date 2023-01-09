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


_ordinal_words = [
    "primero",
    "segundo",
    "tercero",
    "cuarto",
    "quinto",
    "sexto",
    "séptimo",
    "octavo",
    "noveno",
    "décimo",
    "undécimo",
    "duodécimo",
    "decimotercero",
    "decimocuarto",
    "decimoquinto",
    "decimosexto",
    "decimoséptimo",
    "decimoctavo",
    "decimonoveno",
    "vigésimo",
    "trigésimo",
    "cuadragésimo",
    "quincuagésimo",
    "sexagésimo",
    "septuagésimo",
    "octogésima",
    "nonagésima",
    "centésima",
    "milésima",
    "millonésima",
    "billonésima",
]


def like_num(text):
    if text.startswith(("+", "-", "±", "~")):
        text = text[1:]
    text = text.replace(",", "").replace(".", "")
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
    return False


LEX_ATTRS = {LIKE_NUM: like_num}

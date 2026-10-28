from ...attrs import LIKE_NUM

_num_words = [
    "zero",
    "um",
    "uma",
    "dois",
    "duas",
    "três",
    "tres",
    "quatro",
    "cinco",
    "seis",
    "sete",
    "oito",
    "nove",
    "dez",
    "onze",
    "doze",
    "dúzia",
    "dúzias",
    "duzia",
    "duzias",
    "treze",
    "catorze",
    "quinze",
    "dezasseis",
    "dezassete",
    "dezoito",
    "dezanove",
    "vinte",
    "trinta",
    "quarenta",
    "cinquenta",
    "sessenta",
    "setenta",
    "oitenta",
    "noventa",
    "cem",
    "cento",
    "duzentos",
    "duzentas",
    "trezentos",
    "trezentas",
    "quatrocentos",
    "quatrocentas",
    "quinhentos",
    "quinhentas",
    "seiscentos",
    "seiscentas",
    "setecentos",
    "setecentas",
    "oitocentos",
    "oitocentas",
    "novecentos",
    "novecentas",
    "mil",
    "milhão",
    "milhao",
    "milhões",
    "milhoes",
    "bilhão",
    "bilhao",
    "bilhões",
    "bilhoes",
    "trilhão",
    "trilhao",
    "trilhões",
    "trilhoes",
    "quadrilhão",
    "quadrilhao",
    "quadrilhões",
    "quadrilhoes",
]

# Masculine and feminine forms
_ordinal_words = [
    "primeiro",
    "primeira",
    "segundo",
    "segunda",
    "terceiro",
    "terceira",
    "quarto",
    "quarta",
    "quinto",
    "quinta",
    "sexto",
    "sexta",
    "sétimo",
    "séptima",
    "oitavo",
    "oitava",
    "nono",
    "nona",
    "décimo",
    "décima",
    "vigésimo",
    "vigésima",
    "trigésimo",
    "trigésima",
    "quadragésimo",
    "quadragésima",
    "quinquagésimo",
    "quinquagésima",
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
    "ducentésimo",
    "ducentésima",
    "trecentésimo",
    "trecentésima",
    "quadringentésimo",
    "quadringentésima",
    "quingentésimo",
    "quingentésima",
    "sexcentésimo",
    "sexcentésima",
    "septingentésimo",
    "septingentésima",
    "octingentésimo",
    "octingentésima",
    "nongentésimo",
    "nongentésima",
    "milésimo",
    "milésima",
    "milionésimo",
    "milionésima",
    "bilionésimo",
    "bilionésima",
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

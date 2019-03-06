# coding: utf8
from __future__ import unicode_literals

from ...attrs import LIKE_NUM


_num_words = [
    "zero",
    "um",
    "dois",
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
    "trezentos",
    "quatrocentos",
    "quinhentos",
    "seicentos",
    "setecentos",
    "oitocentos",
    "novecentos",
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


_ordinal_words = [
    "primeiro",
    "segundo",
    "terceiro",
    "quarto",
    "quinto",
    "sexto",
    "sétimo",
    "oitavo",
    "nono",
    "décimo",
    "vigésimo",
    "trigésimo",
    "quadragésimo",
    "quinquagésimo",
    "sexagésimo",
    "septuagésimo",
    "octogésimo",
    "nonagésimo",
    "centésimo",
    "ducentésimo",
    "trecentésimo",
    "quadringentésimo",
    "quingentésimo",
    "sexcentésimo",
    "septingentésimo",
    "octingentésimo",
    "nongentésimo",
    "milésimo",
    "milionésimo",
    "bilionésimo",
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
    if text.lower() in _num_words:
        return True
    if text.lower() in _ordinal_words:
        return True
    return False


LEX_ATTRS = {LIKE_NUM: like_num}

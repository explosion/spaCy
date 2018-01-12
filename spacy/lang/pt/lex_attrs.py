# coding: utf8
from __future__ import unicode_literals

from ...attrs import LIKE_NUM


_num_words = ['zero', 'um', 'dois', 'três', 'quatro', 'cinco', 'seis', 'sete',
              'oito', 'nove', 'dez', 'onze', 'doze', 'treze', 'catorze',
              'quinze', 'dezasseis', 'dezassete', 'dezoito', 'dezanove', 'vinte',
              'trinta', 'quarenta', 'cinquenta', 'sessenta', 'setenta',
              'oitenta', 'noventa', 'cem', 'mil', 'milhão', 'bilião', 'trilião',
              'quadrilião']

_ord_words = ['primeiro', 'segundo', 'terceiro', 'quarto', 'quinto', 'sexto',
              'sétimo', 'oitavo', 'nono', 'décimo', 'vigésimo', 'trigésimo',
              'quadragésimo', 'quinquagésimo', 'sexagésimo', 'septuagésimo',
              'octogésimo', 'nonagésimo', 'centésimo', 'ducentésimo',
              'trecentésimo', 'quadringentésimo', 'quingentésimo', 'sexcentésimo',
              'septingentésimo', 'octingentésimo', 'nongentésimo', 'milésimo',
              'milionésimo', 'bilionésimo']


def like_num(text):
    text = text.replace(',', '').replace('.', '')
    if text.isdigit():
        return True
    if text.count('/') == 1:
        num, denom = text.split('/')
        if num.isdigit() and denom.isdigit():
            return True
    if text in _num_words:
        return True
    return False


LEX_ATTRS = {
    LIKE_NUM: like_num
}

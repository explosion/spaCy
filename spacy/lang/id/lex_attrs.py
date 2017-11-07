# coding: utf8
from __future__ import unicode_literals

from ...attrs import LIKE_NUM


_num_words = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven',
              'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen',
              'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty',
              'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety',
              'hundred', 'thousand', 'million', 'billion', 'trillion', 'quadrillion',
              'gajillion', 'bazillion',
              'nol', 'satu', 'dua', 'tiga', 'empat', 'lima', 'enam', 'tujuh',
              'delapan', 'sembilan', 'sepuluh', 'sebelas', 'duabelas', 'tigabelas',
              'empatbelas', 'limabelas', 'enambelas', 'tujuhbelas', 'delapanbelas',
              'sembilanbelas', 'duapuluh', 'seratus', 'seribu', 'sejuta',
              'ribu', 'rb', 'juta', 'jt', 'miliar', 'biliun', 'triliun',
              'kuadriliun', 'kuintiliun', 'sekstiliun', 'septiliun', 'oktiliun',
              'noniliun', 'desiliun']


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
    if text.count('-') == 1:
        _, num = text.split('-')
        if num.isdigit() or num in _num_words:
            return True
    return False


LEX_ATTRS = {
    LIKE_NUM: like_num
}

# coding: utf8
from __future__ import unicode_literals

from ...attrs import LIKE_NUM


_num_words = ['nulis', 'vienas', 'du', 'trys', 'keturi', 'penki', 'šeši', 'septyni',
              'aštuoni', 'devyni', 'dešimt', 'vienuolika', 'dvylika', 'trylika', 'keturiolika',
              'penkiolika', 'šešiolika', 'septyniolika', 'aštuoniolika', 'devyniolika', '',
              'trisdešimt', 'keturiasdešimt', 'penkiasdešimt', 'šešiasdešimt', 'septyniasdešimt', 'aštuoniasdešimt', 'devyniasdešimt',
              'šimtas', 'tūkstantis', 'milijonas', 'milijardas', 'trilijonas', 'kvadrilijonas']


def like_num(text):
    text = text.replace(',', '').replace('.', '')
    if text.isdigit():
        return True
    if text.count('/') == 1:
        num, denom = text.split('/')
        if num.isdigit() and denom.isdigit():
            return True
    if text.lower() in _num_words:
        return True
    return False


LEX_ATTRS = {
    LIKE_NUM: like_num
}

# coding: utf8
from __future__ import unicode_literals

# import the symbols for the attrs you want to overwrite
from ...attrs import LIKE_NUM


# Overwriting functions for lexical attributes
# Documentation: https://localhost:1234/docs/usage/adding-languages#lex-attrs
# Most of these functions, like is_lower or like_url should be language-
# independent. Others, like like_num (which includes both digits and number
# words), requires customisation.


# Example: check if token resembles a number

_num_words = ['sero', 'isa', 'dalawa', 'tatlo', 'apat', 'lima', 'anim', 'pito',
              'walo', 'siyam', 'sampu', 'labing-isa', 'labindalawa', 'labintatlo', 'labing-apat',
              'labinlima', 'labing-anim', 'labimpito', 'labing-walo', 'labinsiyam', 'dalawampu',
              'tatlumpu', 'apatnapu', 'limampu', 'animnapu', 'pitumpu', 'walumpu', 'siyamnapu',
              'daan', 'libo', 'milyon', 'bilyon', 'trilyon', 'quadrilyon',
              'gajilyon', 'bazilyon']


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


# Create dictionary of functions to overwrite. The default lex_attr_getters are
# updated with this one, so only the functions defined here are overwritten.

LEX_ATTRS = {
    LIKE_NUM: like_num
}

# coding: utf8
from __future__ import unicode_literals

from ...attrs import LIKE_NUM

# Source http://mylanguages.org/basque_numbers.php


_num_words = """
bat
bi
hiru
lau
bost
sei
zazpi
zortzi
bederatzi
hamar
hamaika
hamabi
hamahiru
hamalau
hamabost
hamasei
hamazazpi
Hemezortzi
hemeretzi
hogei
ehun
mila
milioi
""".split()

# source https://www.google.com/intl/ur/inputtools/try/

_ordinal_words = """
lehen
bigarren
hirugarren
laugarren
bosgarren
seigarren
zazpigarren
zortzigarren
bederatzigarren
hamargarren
hamaikagarren
hamabigarren
hamahirugarren
hamalaugarren
hamabosgarren
hamaseigarren
hamazazpigarren
hamazortzigarren
hemeretzigarren
hogeigarren
behin
""".split()



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
    if text in _num_words:
        return True
    if text in _ordinal_words:
        return True
    return False


LEX_ATTRS = {LIKE_NUM: like_num}

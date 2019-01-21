# coding: utf-8
from __future__ import unicode_literals


ADVERB_RULES = [
    ["bo$", "by"],
    ["([^hos])nie$", "\\1ny"],
    ["hno$", "hny"],
    ["enie$", "ony"],
    ["śnie$", "sny"],
    ["([gk])o$", "\\1i"],
    ["([bcflmnpswz])io$", "\\1i"],
    ["([cdhpszż])o$", "\\1y"],
    ["([^i])wo$", "\\1wy"],
    ["iwie$", "iwy"],
    ["([^ięrs])to$", "\\1ty"],
    ["([ięr])cie$", "\\1ty"],
    ["ście$", "sty"],
    ["([^d])ro$", "\\1ry"],
    ["drze$", "dry"],
    ["([^bosz])le$", "\\1ły"],
    ["bło$", "bły"],
    ["oło$", "oły"],
    ["śle$", "sły"],
    ["źle$", "zły"],
    ["([^j])mo$", "\\1my"],
    ["jmie$", "jmy"],
]

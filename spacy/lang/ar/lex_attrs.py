# coding: utf8
from __future__ import unicode_literals
from ...attrs import LIKE_NUM

_num_words = set(
    """
صفر
واحد
إثنان
اثنان
ثلاثة
ثلاثه
أربعة
أربعه
خمسة
خمسه
ستة
سته
سبعة
سبعه
ثمانية
ثمانيه
تسعة
تسعه
ﻋﺸﺮﺓ
ﻋﺸﺮه
عشرون
عشرين
ثلاثون
ثلاثين
اربعون
اربعين
أربعون
أربعين
خمسون
خمسين
ستون
ستين
سبعون
سبعين
ثمانون
ثمانين
تسعون
تسعين
مائتين
مائتان
ثلاثمائة
خمسمائة
سبعمائة
الف
آلاف
ملايين
مليون
مليار
مليارات
""".split()
)

_ordinal_words = set(
    """
اول
أول
حاد
واحد
ثان
ثاني
ثالث
رابع
خامس
سادس
سابع
ثامن
تاسع
عاشر
""".split()
)


def like_num(text):
    """
    Check if text resembles a number
    """
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

# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, NORM


_exc = {}


# Time
for exc_data in [
    {NORM: "قبل الميلاد", ORTH: ".ق.م"},
    {NORM: "بعد الميلاد", ORTH: ".ب.م"},
    {NORM: "هجري", ORTH: "هـ"},
    {NORM: "توفي", ORTH: ".ت"},
]:
    _exc[exc_data[ORTH]] = [exc_data]

# Scientific abv.
for exc_data in [
    {NORM: "صلى الله عليه وسلم", ORTH: "صلعم"},
    {NORM: "الشارح", ORTH: "الشـ"},
    {NORM: "الظاهر", ORTH: "الظـ"},
    {NORM: "أيضًا", ORTH: "أيضـ"},
    {NORM: "إلى آخره", ORTH: "إلخ"},
    {NORM: "انتهى", ORTH: "اهـ"},
    {NORM: "حدّثنا", ORTH: "ثنا"},
    {NORM: "أخبرنا", ORTH: "نا"},
    {NORM: "مصدر سابق", ORTH: "م. س"},
    {NORM: "مصدر نفسه", ORTH: "م. ن"},
]:
    _exc[exc_data[ORTH]] = [exc_data]

# Titles
for exc_data in [
    {NORM: "دكتور", ORTH: "د."},
    {NORM: "أستاذ دكتور", ORTH: "أ.د"},
    {NORM: "أستاذ", ORTH: "أ."},
    {NORM: "بروفيسور", ORTH: "ب."},
    {NORM: "مهندس", ORTH: ".م"},
]:
    _exc[exc_data[ORTH]] = [exc_data]

for exc_data in [{NORM: "تلفون", ORTH: "ت."}, {NORM: "صندوق بريد", ORTH: "ص.ب"}]:
    _exc[exc_data[ORTH]] = [exc_data]

TOKENIZER_EXCEPTIONS = _exc

# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, TAG, NORM, PRON_LEMMA
import re

_exc = {}

# time
for exc_data in [
    {LEMMA: "قبل الميلاد", ORTH: "ق.م"},
    {LEMMA: "بعد الميلاد", ORTH: "ب. م"},
    {LEMMA: "ميلادي", ORTH: ".م"},
    {LEMMA: "هجري", ORTH: ".هـ"},
    {LEMMA: "توفي", ORTH: ".ت"}]:
    _exc[exc_data[ORTH]] = [exc_data]

# scientific abv.
for exc_data in [
    {LEMMA: "صلى الله عليه وسلم", ORTH: "صلعم"},
    {LEMMA: "الشارح", ORTH: "الشـ"},
    {LEMMA: "الظاهر", ORTH: "الظـ"},
    {LEMMA: "أيضًا", ORTH: "أيضـ"},
    {LEMMA: "إلى آخره", ORTH: "إلخ"},
    {LEMMA: "انتهى", ORTH: "اهـ"},
    {LEMMA: "حدّثنا", ORTH: "ثنا"},
    {LEMMA: "حدثني", ORTH: "ثنى"},
    {LEMMA: "أنبأنا", ORTH: "أنا"},
    {LEMMA: "أخبرنا", ORTH: "نا"},
    {LEMMA: "مصدر سابق", ORTH: "م. س"},
    {LEMMA: "مصدر نفسه", ORTH: "م. ن"}]:
    _exc[exc_data[ORTH]] = [exc_data]

# other abv.
for exc_data in [
    {LEMMA: "دكتور", ORTH: "د."},
    {LEMMA: "أستاذ دكتور", ORTH: "أ.د"},
    {LEMMA: "أستاذ", ORTH: "أ."},
    {LEMMA: "بروفيسور", ORTH: "ب."}]:
    _exc[exc_data[ORTH]] = [exc_data]

for exc_data in [
    {LEMMA: "تلفون", ORTH: "ت."},
    {LEMMA: "صندوق بريد", ORTH: "ص.ب"}]:
    _exc[exc_data[ORTH]] = [exc_data]

TOKENIZER_EXCEPTIONS = _exc

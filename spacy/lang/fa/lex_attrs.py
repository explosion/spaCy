# coding: utf8
from __future__ import unicode_literals
from ...attrs import LIKE_NUM


MIM = "م"
ZWNJ_O_MIM = "‌ام"
YE_NUN = "ین"


_num_words = set(
    """
صفر
یک
دو
سه
چهار
پنج
شش
شیش
هفت
هشت
نه
ده
یازده
دوازده
سیزده
چهارده
پانزده
پونزده
شانزده
شونزده
هفده
هجده
هیجده
نوزده
بیست
سی
چهل
پنجاه
شصت
هفتاد
هشتاد
نود
صد
یکصد
یک‌صد
دویست
سیصد
چهارصد
پانصد
پونصد
ششصد
شیشصد
هفتصد
هفصد
هشتصد
نهصد
هزار
میلیون
میلیارد
بیلیون
بیلیارد
تریلیون
تریلیارد
کوادریلیون
کادریلیارد
کوینتیلیون
""".split()
)

_ordinal_words = set(
    """
اول
سوم
سی‌ام""".split()
)

_ordinal_words.update({num + MIM for num in _num_words})
_ordinal_words.update({num + ZWNJ_O_MIM for num in _num_words})
_ordinal_words.update({num + YE_NUN for num in _ordinal_words})


def like_num(text):
    """
    check if text resembles a number
    """
    text = (
        text.replace(",", "")
        .replace(".", "")
        .replace("،", "")
        .replace("٫", "")
        .replace("/", "")
    )
    if text.isdigit():
        return True
    if text in _num_words:
        return True
    if text in _ordinal_words:
        return True
    return False


LEX_ATTRS = {LIKE_NUM: like_num}

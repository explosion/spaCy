# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, NORM, PRON_LEMMA


_exc = {}


for exc_data in [
    {ORTH: "ት/ቤት", LEMMA: "ትምህርት ቤት"},
    {ORTH: "ጽ/ቤት", LEMMA: "ጽህፈት ቤት", NORM: "ጽህፈት ቤት"},
    {ORTH: "ፅ/ቤት", LEMMA: "ጽህፈት ቤት", NORM: "ጽህፈት ቤት"},
    {ORTH: "መ/ቤት", LEMMA: "መስሪያ ቤት", NORM: "መስሪያ ቤት"},
    {ORTH: "ም/ቤት", LEMMA: "ምክር ቤት", NORM: "ምክር ቤት"},
    {ORTH: "ፍ/ቤት", LEMMA: "ፍርድ ቤት", NORM: "ፍርድ ቤት"},
     {ORTH: "ቤ/ክ", LEMMA: "ቤተክርስቲያን", NORM: "ቤተክርስቲያን"},
    {ORTH: "ቤ/መ.", LEMMA: "ቤተመንግስት", NORM: "ቤተመንግስት"},
    {ORTH: "ሆ/ል", LEMMA: "ሆስፒታል", NORM: "ሆስፒታል"},
    {ORTH: "ዶ/ር", LEMMA: "ዶክተር", NORM: "ዶክተር"},
    {ORTH: "ፕ/ሮ", LEMMA: "ፕሮፌሰር", NORM: "ፕሮፌሰር"},
    {ORTH: "ጠ/ሚ", LEMMA: "ጠቅላይ ሚኒስተር", NORM: "ጠቅላይ ሚኒስተር"},
    {ORTH: "ጠ/ሚኒስተር", LEMMA: "ጠቅላይ ሚኒስተር", NORM: "ጠቅላይ ሚኒስተር"},
    {ORTH: "ጠ/ሚ/ቢሮ", LEMMA: "ጠቅላይ ሚኒስተር ቢሮ", NORM: "ጠቅላይ ሚኒስተር ቢሮ"},
    {ORTH: "ሚ/ሩ", LEMMA: "ሚኒስትሩ", NORM: "ሚኒስትሩ"},
    {ORTH: "ኮ/ል", LEMMA: "ኮለኔል", NORM: "ኮለኔል"},
    {ORTH: "ጄ/ል", LEMMA: "ጄኔራል", NORM: "ጄኔራል"},
    {ORTH: "ሻ/ል", LEMMA: "ሻምበል", NORM: "ሻምበል"},
    {ORTH: "አ/ም", LEMMA: "አመተ ምህረት", NORM: "አመተ ምህረት"},
    {ORTH: "ዓ/ም", LEMMA: "ዓመተ ምህረት", NORM: "ዓመተ ምህረት"},
    {ORTH: "አ.ም", LEMMA: "አመተ ምህረት", NORM: "አመተ ምህረት"},
    {ORTH: "ዓ.ም", LEMMA: "ዓመተ ምህረት", NORM: "ዓመተ ምህረት"},
    {ORTH: "ዓ/ዓ", LEMMA: "ዓመተ ዓለም", NORM: "ዓመተ ዓለም"},
    {ORTH: "አ/አ", LEMMA: "አመተ አለም", NORM: "አመተ አለም"},
    {ORTH: "አ/ማ", LEMMA: "አክሲዮን ማህበር", NORM: "አክሲዮን ማህበር"},  
    {ORTH: "ወ/ሮ", LEMMA: PRON_LEMMA, NORM: "ወይዘሮ"},

]:
    _exc[exc_data[ORTH]] = [exc_data]


for orth in [
    "ዓ.ም.",
    "ኪ.ሜ.",
]:
    _exc[orth] = [{ORTH: orth}]


TOKENIZER_EXCEPTIONS = _exc

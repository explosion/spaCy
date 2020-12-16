# coding: utf8
from __future__ import unicode_literals

import re

from ..punctuation import ALPHA_LOWER, ALPHA
from ...symbols import ORTH, LEMMA, NORM

_exc = {}


_abbr_period_exc = [
    {ORTH: "A.B.D.", LEMMA: "Amerika Birleşik Devletleri", NORM: "Amerika"},
    {ORTH: "Alb.", LEMMA: "albay", NORM: "albay"},
    {ORTH: "Ank.", LEMMA: "Ankara", NORM: "Ankara"},
    {ORTH: "Ar.Gör.", LEMMA: "araştırma görevlisi"},
    {ORTH: "Arş.Gör.", LEMMA: "araştırma görevlisi"},
    {ORTH: "Asb.", LEMMA: "astsubay", NORM: "astsubay"},
    {ORTH: "Astsb.", LEMMA: "astsubay", NORM: "astsubay"},
    {ORTH: "As.İz.", LEMMA: "askeri inzibat"},
    {ORTH: "as.iz.", LEMMA: "askeri inzibat"},
    {ORTH: "Atğm", LEMMA: "asteğmen", NORM: "asteğmen"},
    {ORTH: "Av.", LEMMA: "avukat", NORM: "avukat"},
    {ORTH: "Apt.", LEMMA: "apartmanı", NORM: "apartmanı"},
    {ORTH: "apt.", LEMMA: "apartmanı", NORM: "apartmanı"},
    {ORTH: "Bçvş.", LEMMA: "başçavuş", NORM: "başçavuş"},
    {ORTH: "bçvş.", LEMMA: "başçavuş", NORM: "başçavuş"},
    {ORTH: "bk.", LEMMA: "bakınız", NORM: "bakınız"},
    {ORTH: "bknz.", LEMMA: "bakınız", NORM: "bakınız"},
    {ORTH: "Bnb.", LEMMA: "binbaşı", NORM: "binbaşı"},
    {ORTH: "bnb.", LEMMA: "binbaşı", NORM: "binbaşı"},
    {ORTH: "Böl.", LEMMA: "bölümü", NORM: "bölümü"},
    {ORTH: "böl.", LEMMA: "bölümü", NORM: "bölümü"},
    {ORTH: "Bşk.", LEMMA: "başkanlığı", NORM: "başkanlığı"},
    {ORTH: "bşk.", LEMMA: "başkanlığı", NORM: "başkanlığı"},
    {ORTH: "Bştbp.", LEMMA: "baştabip", NORM: "baştabip"},
    {ORTH: "bştbp.", LEMMA: "baştabip", NORM: "baştabip"},
    {ORTH: "Bul.", LEMMA: "bulvarı", NORM: "bulvarı"},
    {ORTH: "bul.", LEMMA: "bulvarı", NORM: "bulvarı"},
    {ORTH: "Cad.", LEMMA: "caddesi", NORM: "caddesi"},
    {ORTH: "cad.", LEMMA: "caddesi", NORM: "caddesi"},
    {ORTH: "çev.", LEMMA: "çeviren", NORM: "çeviren"},
    {ORTH: "Çvş.", LEMMA: "çavuş", NORM: "çavuş"},
    {ORTH: "çvş.", LEMMA: "çavuş", NORM: "çavuş"},
    {ORTH: "dak.", LEMMA: "dakika", NORM: "dakika"},
    {ORTH: "dk.", LEMMA: "dakika", NORM: "dakika"},
    {ORTH: "Doç.", LEMMA: "doçent", NORM: "doçent"},
    {ORTH: "doğ.", LEMMA: "doğum tarihi"},
    {ORTH: "Dr.", LEMMA: "doktor", NORM: "doktor"},
    {ORTH: "dr.", LEMMA: "doktor", NORM:"doktor"},
    {ORTH: "drl.", LEMMA: "derleyen", NORM: "derleyen"},
    {ORTH: "Dz.", LEMMA: "deniz", NORM: "deniz"},
    {ORTH: "Dz.K.K.lığı", LEMMA: "Deniz Kuvvetleri Komutanlığı"},
    {ORTH: "Dz.Kuv.", LEMMA: "Deniz Kuvvetleri"},
    {ORTH: "Dz.Kuv.K.", LEMMA: "Deniz Kuvvetleri Komutanlığı"},
    {ORTH: "dzl.", LEMMA: "düzenleyen", NORM: "düzenleyen"},
    {ORTH: "Ecz.", LEMMA: "eczanesi", NORM: "eczanesi"},
    {ORTH: "ecz.", LEMMA: "eczanesi", NORM: "eczanesi"},
    {ORTH: "ekon.", LEMMA: "ekonomi", NORM: "ekonomi"},
    {ORTH: "Fak.", LEMMA: "fakültesi", NORM: "fakültesi"},
    {ORTH: "Gn.", LEMMA: "genel", NORM: "genel"},
    {ORTH: "Gnkur.", LEMMA: "Genelkurmay", NORM: "Genelkurmay"},
    {ORTH: "Gn.Kur.", LEMMA: "Genelkurmay", NORM: "Genelkurmay"},
    {ORTH: "gr.", LEMMA: "gram", NORM: "gram"},
    {ORTH: "Hst.", LEMMA: "hastanesi", NORM: "hastanesi"},
    {ORTH: "hst.", LEMMA: "hastanesi", NORM: "hastanesi"},
    {ORTH: "Hs.Uzm.", LEMMA: "hesap uzmanı"},
    {ORTH: "huk.", LEMMA: "hukuk", NORM: "hukuk"},
    {ORTH: "Hv.", LEMMA: "hava", NORM: "hava"},
    {ORTH: "Hv.K.K.lığı", LEMMA: "Hava Kuvvetleri Komutanlığı"},
    {ORTH: "Hv.Kuv.", LEMMA: "Hava Kuvvetleri"},
    {ORTH: "Hv.Kuv.K.", LEMMA: "Hava Kuvvetleri Komutanlığı"},
    {ORTH: "Hz.", LEMMA: "hazreti", NORM: "hazreti"},
    {ORTH: "Hz.Öz.", LEMMA: "hizmete özel"},
    {ORTH: "İng.", LEMMA: "ingilizce", NORM: "ingilizce"},
    {ORTH: "İst.", LEMMA: "İstanbul", NORM: "İstanbul"},
    {ORTH: "Jeol.", LEMMA: "jeoloji", NORM: "jeoloji"},
    {ORTH: "jeol.", LEMMA: "jeoloji", NORM: "jeoloji"},
    {ORTH: "Korg.", LEMMA: "korgeneral", NORM: "korgeneral"},
    {ORTH: "Kur.", LEMMA: "kurmay", NORM: "kurmay"},
    {ORTH: "Kur.Bşk.", LEMMA: "kurmay başkanı"},
    {ORTH: "Kuv.", LEMMA: "kuvvetleri", NORM: "kuvvetleri"},
    {ORTH: "Ltd.", LEMMA: "limited", NORM: "limited"},
    {ORTH: "ltd.", LEMMA: "limited", NORM: "limited"},
    {ORTH: "Mah.", LEMMA: "mahallesi", NORM: "mahallesi"},
    {ORTH: "mah.", LEMMA: "mahallesi", NORM: "mahallesi"},
    {ORTH: "max.", LEMMA: "maksimum", NORM: "maksimum"},
    {ORTH: "min.", LEMMA: "minimum", NORM: "minimum"},
    {ORTH: "Müh.", LEMMA: "mühendisliği", NORM: "mühendisliği"},
    {ORTH: "müh.", LEMMA: "mühendisliği", NORM: "mühendisliği"},
    {ORTH: "M.Ö.", LEMMA: "milattan önce"},
    {ORTH: "M.S.", LEMMA: "milattan sonra"},
    {ORTH: "Onb.", LEMMA: "onbaşı", NORM: "onbaşı"},
    {ORTH: "Ord.", LEMMA: "ordinaryüs", NORM: "ordinaryüs"},
    {ORTH: "Org.", LEMMA: "orgeneral", NORM: "orgeneral"},
    {ORTH: "Ped.", LEMMA: "pedagoji", NORM: "pedagoji"},
    {ORTH: "Prof.", LEMMA: "profesör", NORM: "profesör"},
    {ORTH: "prof.", LEMMA: "profesör", NORM: "profesör"},
    {ORTH: "Sb.", LEMMA: "subay", NORM: "subay"},
    {ORTH: "Sn.", LEMMA: "sayın", NORM: "sayın"},
    {ORTH: "sn.", LEMMA: "saniye", NORM: "saniye"},
    {ORTH: "Sok.", LEMMA: "sokak", NORM: "sokak"},
    {ORTH: "sok.", LEMMA: "sokak", NORM: "sokak"},
    {ORTH: "Şb.", LEMMA: "şube", NORM: "şube"},
    {ORTH: "şb.", LEMMA: "şube", NORM: "şube"},
    {ORTH: "Şti.", LEMMA: "şirketi", NORM: "şirketi"},
    {ORTH: "şti.", LEMMA: "şirketi", NORM: "şirketi"},
    {ORTH: "Tbp.", LEMMA: "tabip", NORM: "tabip"},
    {ORTH: "tbp.", LEMMA: "tabip", NORM: "tabip"},
    {ORTH: "T.C.", LEMMA: "Türkiye Cumhuriyeti"},
    {ORTH: "Tel.", LEMMA: "telefon", NORM: "telefon"},
    {ORTH: "tel.", LEMMA: "telefon", NORM: "telefon"},
    {ORTH: "telg.", LEMMA: "telgraf", NORM: "telgraf"},
    {ORTH: "Tğm.", LEMMA: "teğmen", NORM: "teğmen"},
    {ORTH: "tğm.", LEMMA: "teğmen", NORM: "teğmen"},
    {ORTH: "tic.", LEMMA: "ticaret", NORM: "ticaret"},
    {ORTH: "Tug.", LEMMA: "tugay", NORM: "tugay"},
    {ORTH: "Tuğg.", LEMMA: "tuğgeneral", NORM: "tuğgeneral"},
    {ORTH: "Tümg.", LEMMA: "tümgeneral", NORM: "tümgeneral"},
    {ORTH: "Uzm.", LEMMA: "uzman", NORM: "uzman"},
    {ORTH: "Üçvş.", LEMMA: "üstçavuş", NORM: "üstçavuş"},
    {ORTH: "Üni.", LEMMA: "üniversitesi", NORM: "üniversitesi"},
    {ORTH: "Ütğm.", LEMMA: "üsteğmen", NORM:  "üsteğmen"},
    {ORTH: "vb.", LEMMA: "ve benzeri"},
    {ORTH: "vs.", LEMMA: "vesaire", NORM: "vesaire"},
    {ORTH: "Yard.", LEMMA: "yardımcı", NORM: "yardımcı"},
    {ORTH: "Yar.", LEMMA: "yardımcı", NORM: "yardımcı"},
    {ORTH: "Yd.Sb.", LEMMA: "yedek subay"},
    {ORTH: "Yard.Doç.", LEMMA: "yardımcı doçent"},
    {ORTH: "Yar.Doç.", LEMMA: "yardımcı doçent"},
    {ORTH: "Yb.", LEMMA: "yarbay", NORM: "yarbay"},
    {ORTH: "Yrd.", LEMMA: "yardımcı", NORM: "yardımcı"},
    {ORTH: "Yrd.Doç.", LEMMA: "yardımcı doçent"},
    {ORTH: "Y.Müh.", LEMMA: "yüksek mühendis"},
    {ORTH: "Y.Mim.", LEMMA: "yüksek mimar"},
    {ORTH: "yy.", LEMMA: "yüzyıl", NORM: "yüzyıl"},
]

for abbr in _abbr_period_exc:
    _exc[abbr[ORTH]] = [abbr]

_abbr_exc = [
    {ORTH: "AB", LEMMA: "Avrupa Birliği", NORM: "Avrupa Birliği"},
    {ORTH: "ABD", LEMMA: "Amerika Birleşik Devletleri", NORM: "Amerika"},
    {ORTH: "ABS", LEMMA: "fren", NORM: "fren"},
    {ORTH: "AOÇ", LEMMA: "Atatürk orman çiftliği"},
    {ORTH: "ASKİ", LEMMA: "Ankara su ve kanalizasyon idaresi"},
    {ORTH: "Bağ-kur", LEMMA: "Bağkur", NORM: "Bağkur"},
    {ORTH: "BDDK", LEMMA: "bankacılık düzenleme ve denetleme kurumu"},
    {ORTH: "BJK", LEMMA: "Beşiktaş", NORM: "Beşiktaş"},
    {ORTH: "ESA", LEMMA: "Avrupa uzay ajansı", NORM: "Avrupa uzay ajansı"},
    {ORTH: "FB", LEMMA: "Fenerbahçe", NORM: "Fenerbahçe"},
    {ORTH: "GATA", LEMMA: "Gülhane askeri tıp akademisi"},
    {ORTH: "GS", LEMMA: "Galatasaray", NORM: "Galatasaray"},
    {ORTH: "İSKİ", LEMMA: "İstanbul su ve kanalizasyon idaresi"},
    {ORTH: "KBB", LEMMA: "kulak burun boğaz"},
    {ORTH: "RTÜK", LEMMA: "radyo ve televizyon üst kurulu", NORM: "radyo ve televizyon üst kurulu"},
    {ORTH: "TBMM", LEMMA: "Türkiye Büyük Millet Meclisi"},
    {ORTH: "TC", LEMMA: "Türkiye Cumhuriyeti"},
    {ORTH: "TÜİK", LEMMA: "Türkiye istatistik kurumu", NORM: "Türkiye istatistik kurumu"},
    {ORTH: "YÖK", LEMMA: "Yüksek Öğrenim Kurumu"},
]

for abbr in _abbr_exc:
    _exc[abbr[ORTH]] = [abbr]



_num = r"[+-]?\d+([,.]\d+)*"
_ord_num = r"(\d+\.)"
_date = r"(((\d{1,2}[./-]){2})?(\d{4})|(\d{1,2}[./]\d{1,2}(\.)?))"
_dash_num = r"(([{al}\d]+/\d+)|(\d+/[{al}]))".format(al=ALPHA)
_roman_num =  "M{0,3}(?:C[MD]|D?C{0,3})(?:X[CL]|L?X{0,3})(?:I[XV]|V?I{0,3})"
_roman_ord = r"({rn})\.".format(rn=_roman_num)
_time_exp = r"\d+(:\d+)*"

_inflections = r"'[{al}]+".format(al=ALPHA_LOWER)
_abbrev_inflected = r"[{a}]+\.'[{al}]+".format(a=ALPHA, al=ALPHA_LOWER)

_nums = r"(({d})|({dn})|({te})|({on})|({n})|({ro})|({rn}))({inf})?".format(d=_date, dn=_dash_num, te=_time_exp, on=_ord_num, n=_num, ro=_roman_ord, rn=_roman_num, inf=_inflections)

TOKENIZER_EXCEPTIONS = _exc
TOKEN_MATCH = re.compile(r"^({abbr})|({n})$".format(n=_nums, abbr=_abbrev_inflected)).match

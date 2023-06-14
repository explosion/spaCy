import re

from ...symbols import NORM, ORTH
from ..punctuation import ALPHA, ALPHA_LOWER

_exc = {}


_abbr_period_exc = [
    {ORTH: "A.B.D.", NORM: "Amerika"},
    {ORTH: "Alb.", NORM: "albay"},
    {ORTH: "Ank.", NORM: "Ankara"},
    {ORTH: "Ar.Gör."},
    {ORTH: "Arş.Gör."},
    {ORTH: "Asb.", NORM: "astsubay"},
    {ORTH: "Astsb.", NORM: "astsubay"},
    {ORTH: "As.İz."},
    {ORTH: "as.iz."},
    {ORTH: "Atğm", NORM: "asteğmen"},
    {ORTH: "Av.", NORM: "avukat"},
    {ORTH: "Apt.", NORM: "apartmanı"},
    {ORTH: "apt.", NORM: "apartmanı"},
    {ORTH: "Bçvş.", NORM: "başçavuş"},
    {ORTH: "bçvş.", NORM: "başçavuş"},
    {ORTH: "bk.", NORM: "bakınız"},
    {ORTH: "bknz.", NORM: "bakınız"},
    {ORTH: "Bnb.", NORM: "binbaşı"},
    {ORTH: "bnb.", NORM: "binbaşı"},
    {ORTH: "Böl.", NORM: "bölümü"},
    {ORTH: "böl.", NORM: "bölümü"},
    {ORTH: "Bşk.", NORM: "başkanlığı"},
    {ORTH: "bşk.", NORM: "başkanlığı"},
    {ORTH: "Bştbp.", NORM: "baştabip"},
    {ORTH: "bştbp.", NORM: "baştabip"},
    {ORTH: "Bul.", NORM: "bulvarı"},
    {ORTH: "bul.", NORM: "bulvarı"},
    {ORTH: "Cad.", NORM: "caddesi"},
    {ORTH: "cad.", NORM: "caddesi"},
    {ORTH: "çev.", NORM: "çeviren"},
    {ORTH: "Çvş.", NORM: "çavuş"},
    {ORTH: "çvş.", NORM: "çavuş"},
    {ORTH: "dak.", NORM: "dakika"},
    {ORTH: "dk.", NORM: "dakika"},
    {ORTH: "Doç.", NORM: "doçent"},
    {ORTH: "doğ."},
    {ORTH: "Dr.", NORM: "doktor"},
    {ORTH: "dr.", NORM: "doktor"},
    {ORTH: "drl.", NORM: "derleyen"},
    {ORTH: "Dz.", NORM: "deniz"},
    {ORTH: "Dz.K.K.lığı"},
    {ORTH: "Dz.Kuv."},
    {ORTH: "Dz.Kuv.K."},
    {ORTH: "dzl.", NORM: "düzenleyen"},
    {ORTH: "Ecz.", NORM: "eczanesi"},
    {ORTH: "ecz.", NORM: "eczanesi"},
    {ORTH: "ekon.", NORM: "ekonomi"},
    {ORTH: "Fak.", NORM: "fakültesi"},
    {ORTH: "Gn.", NORM: "genel"},
    {ORTH: "Gnkur.", NORM: "Genelkurmay"},
    {ORTH: "Gn.Kur.", NORM: "Genelkurmay"},
    {ORTH: "gr.", NORM: "gram"},
    {ORTH: "Hst.", NORM: "hastanesi"},
    {ORTH: "hst.", NORM: "hastanesi"},
    {ORTH: "Hs.Uzm."},
    {ORTH: "huk.", NORM: "hukuk"},
    {ORTH: "Hv.", NORM: "hava"},
    {ORTH: "Hv.K.K.lığı"},
    {ORTH: "Hv.Kuv."},
    {ORTH: "Hv.Kuv.K."},
    {ORTH: "Hz.", NORM: "hazreti"},
    {ORTH: "Hz.Öz."},
    {ORTH: "İng.", NORM: "ingilizce"},
    {ORTH: "İst.", NORM: "İstanbul"},
    {ORTH: "Jeol.", NORM: "jeoloji"},
    {ORTH: "jeol.", NORM: "jeoloji"},
    {ORTH: "Korg.", NORM: "korgeneral"},
    {ORTH: "Kur.", NORM: "kurmay"},
    {ORTH: "Kur.Bşk."},
    {ORTH: "Kuv.", NORM: "kuvvetleri"},
    {ORTH: "Ltd.", NORM: "limited"},
    {ORTH: "ltd.", NORM: "limited"},
    {ORTH: "Mah.", NORM: "mahallesi"},
    {ORTH: "mah.", NORM: "mahallesi"},
    {ORTH: "max.", NORM: "maksimum"},
    {ORTH: "min.", NORM: "minimum"},
    {ORTH: "Müh.", NORM: "mühendisliği"},
    {ORTH: "müh.", NORM: "mühendisliği"},
    {ORTH: "M.Ö."},
    {ORTH: "M.S."},
    {ORTH: "Onb.", NORM: "onbaşı"},
    {ORTH: "Ord.", NORM: "ordinaryüs"},
    {ORTH: "Org.", NORM: "orgeneral"},
    {ORTH: "Ped.", NORM: "pedagoji"},
    {ORTH: "Prof.", NORM: "profesör"},
    {ORTH: "prof.", NORM: "profesör"},
    {ORTH: "Sb.", NORM: "subay"},
    {ORTH: "Sn.", NORM: "sayın"},
    {ORTH: "sn.", NORM: "saniye"},
    {ORTH: "Sok.", NORM: "sokak"},
    {ORTH: "sok.", NORM: "sokak"},
    {ORTH: "Şb.", NORM: "şube"},
    {ORTH: "şb.", NORM: "şube"},
    {ORTH: "Şti.", NORM: "şirketi"},
    {ORTH: "şti.", NORM: "şirketi"},
    {ORTH: "Tbp.", NORM: "tabip"},
    {ORTH: "tbp.", NORM: "tabip"},
    {ORTH: "T.C."},
    {ORTH: "Tel.", NORM: "telefon"},
    {ORTH: "tel.", NORM: "telefon"},
    {ORTH: "telg.", NORM: "telgraf"},
    {ORTH: "Tğm.", NORM: "teğmen"},
    {ORTH: "tğm.", NORM: "teğmen"},
    {ORTH: "tic.", NORM: "ticaret"},
    {ORTH: "Tug.", NORM: "tugay"},
    {ORTH: "Tuğg.", NORM: "tuğgeneral"},
    {ORTH: "Tümg.", NORM: "tümgeneral"},
    {ORTH: "Uzm.", NORM: "uzman"},
    {ORTH: "Üçvş.", NORM: "üstçavuş"},
    {ORTH: "Üni.", NORM: "üniversitesi"},
    {ORTH: "Ütğm.", NORM: "üsteğmen"},
    {ORTH: "vb."},
    {ORTH: "vs.", NORM: "vesaire"},
    {ORTH: "Yard.", NORM: "yardımcı"},
    {ORTH: "Yar.", NORM: "yardımcı"},
    {ORTH: "Yd.Sb."},
    {ORTH: "Yard.Doç."},
    {ORTH: "Yar.Doç."},
    {ORTH: "Yb.", NORM: "yarbay"},
    {ORTH: "Yrd.", NORM: "yardımcı"},
    {ORTH: "Yrd.Doç."},
    {ORTH: "Y.Müh."},
    {ORTH: "Y.Mim."},
    {ORTH: "yy.", NORM: "yüzyıl"},
]

for abbr in _abbr_period_exc:
    _exc[abbr[ORTH]] = [abbr]

_abbr_exc = [
    {ORTH: "AB", NORM: "Avrupa Birliği"},
    {ORTH: "ABD", NORM: "Amerika"},
    {ORTH: "ABS", NORM: "fren"},
    {ORTH: "AOÇ"},
    {ORTH: "ASKİ"},
    {ORTH: "Bağ-kur", NORM: "Bağkur"},
    {ORTH: "BDDK"},
    {ORTH: "BJK", NORM: "Beşiktaş"},
    {ORTH: "ESA", NORM: "Avrupa uzay ajansı"},
    {ORTH: "FB", NORM: "Fenerbahçe"},
    {ORTH: "GATA"},
    {ORTH: "GS", NORM: "Galatasaray"},
    {ORTH: "İSKİ"},
    {ORTH: "KBB"},
    {ORTH: "RTÜK", NORM: "radyo ve televizyon üst kurulu"},
    {ORTH: "TBMM"},
    {ORTH: "TC"},
    {ORTH: "TÜİK", NORM: "Türkiye istatistik kurumu"},
    {ORTH: "YÖK"},
]

for abbr in _abbr_exc:
    _exc[abbr[ORTH]] = [abbr]


_num = r"[+-]?\d+([,.]\d+)*"
_ord_num = r"(\d+\.)"
_date = r"(((\d{1,2}[./-]){2})?(\d{4})|(\d{1,2}[./]\d{1,2}(\.)?))"
_dash_num = r"(([{al}\d]+/\d+)|(\d+/[{al}]))".format(al=ALPHA)
_roman_num = "M{0,3}(?:C[MD]|D?C{0,3})(?:X[CL]|L?X{0,3})(?:I[XV]|V?I{0,3})"
_roman_ord = r"({rn})\.".format(rn=_roman_num)
_time_exp = r"\d+(:\d+)*"

_inflections = r"'[{al}]+".format(al=ALPHA_LOWER)
_abbrev_inflected = r"[{a}]+\.'[{al}]+".format(a=ALPHA, al=ALPHA_LOWER)

_nums = r"(({d})|({dn})|({te})|({on})|({n})|({ro})|({rn}))({inf})?".format(
    d=_date,
    dn=_dash_num,
    te=_time_exp,
    on=_ord_num,
    n=_num,
    ro=_roman_ord,
    rn=_roman_num,
    inf=_inflections,
)

TOKENIZER_EXCEPTIONS = _exc
TOKEN_MATCH = re.compile(
    r"^({abbr})|({n})$".format(n=_nums, abbr=_abbrev_inflected)
).match

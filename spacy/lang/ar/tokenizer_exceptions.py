from ...symbols import NORM, ORTH
from ...util import update_exc
from ..tokenizer_exceptions import BASE_EXCEPTIONS

_exc = {}


# Time
for exc_data in [
    {NORM: "قبل الميلاد", ORTH: "ق.م"},
    {NORM: "بعد الميلاد", ORTH: "ب. م"},
    {NORM: "ميلادي", ORTH: ".م"},
    {NORM: "هجري", ORTH: ".هـ"},
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
    {NORM: "حدثني", ORTH: "ثنى"},
    {NORM: "أنبأنا", ORTH: "أنا"},
    {NORM: "أخبرنا", ORTH: "نا"},
    {NORM: "مصدر سابق", ORTH: "م. س"},
    {NORM: "مصدر نفسه", ORTH: "م. ن"},
]:
    _exc[exc_data[ORTH]] = [exc_data]

# Other abv.
for exc_data in [
    {NORM: "دكتور", ORTH: "د."},
    {NORM: "أستاذ دكتور", ORTH: "أ.د"},
    {NORM: "أستاذ", ORTH: "أ."},
    {NORM: "بروفيسور", ORTH: "ب."},
]:
    _exc[exc_data[ORTH]] = [exc_data]

for exc_data in [{NORM: "تلفون", ORTH: "ت."}, {NORM: "صندوق بريد", ORTH: "ص.ب"}]:
    _exc[exc_data[ORTH]] = [exc_data]

TOKENIZER_EXCEPTIONS = update_exc(BASE_EXCEPTIONS, _exc)

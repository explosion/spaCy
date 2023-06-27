from ...symbols import NORM, ORTH
from ...util import update_exc
from ..tokenizer_exceptions import BASE_EXCEPTIONS

_exc = {}


for exc_data in [
    {ORTH: "ডঃ", NORM: "ডক্টর"},
    {ORTH: "ডাঃ", NORM: "ডাক্তার"},
    {ORTH: "ড.", NORM: "ডক্টর"},
    {ORTH: "ডা.", NORM: "ডাক্তার"},
    {ORTH: "মোঃ", NORM: "মোহাম্মদ"},
    {ORTH: "মো.", NORM: "মোহাম্মদ"},
    {ORTH: "সে.", NORM: "সেলসিয়াস"},
    {ORTH: "কি.মি.", NORM: "কিলোমিটার"},
    {ORTH: "কি.মি", NORM: "কিলোমিটার"},
    {ORTH: "সে.মি.", NORM: "সেন্টিমিটার"},
    {ORTH: "সে.মি", NORM: "সেন্টিমিটার"},
    {ORTH: "মি.লি.", NORM: "মিলিলিটার"},
]:
    _exc[exc_data[ORTH]] = [exc_data]


TOKENIZER_EXCEPTIONS = update_exc(BASE_EXCEPTIONS, _exc)

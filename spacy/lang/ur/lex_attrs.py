from ...attrs import LIKE_NUM

# Cardinal forms. Existing entries are retained (including historical
# orthographic variants). Standard missing forms follow:
# https://en.wikibooks.org/wiki/Urdu/Vocabulary/Numbers
# https://www.urdu-english.com/lessons/beginner/numbers
# Indian numbering units: https://en.wikipedia.org/wiki/Indian_numbering_system
# fmt: off
_num_words = set(
    """
صفر
ایک دو تین چار پانچ چھ چھے سات آٹھ نو دس
گیارہ بارہ تیرہ چودہ پندرہ سولہ سترہ اٹھارہ اٹھارا اٹهارا انیس
بیس اکیس بائیس تئیس چوبیس پچیس چھبیس چھببیس
ستایس ستائیس اٹھائس اٹھائیس انتيس انتیس
تیس اکتیس بتیس تینتیس چونتیس پینتیس
چھتیس سینتیس ارتیس اڑتیس انتالیس
چالیس اکتالیس بیالیس تیتالیس چوالیس پیتالیس پینتالیس
چھیالیس سینتالیس اڑتالیس انچالیس انچاس
پچاس اکاون باون تریپن چون پچپن چھپن ستاون اٹھاون انسٹھ
ساثھ ساٹھ
اکسٹھ باسٹھ تریسٹھ چوسٹھ پیسٹھ چھیاسٹھ سڑسٹھ اڑسٹھ
انھتر انہتر ستر اکھتر اکہتر بھتتر بہتر تیھتر تہتر
چوھتر چوہتر تچھتر پچہتر چھیتر چھہتر ستتر
اٹھتر انیاسی اناسی اسی اکیاسی بیاسی تیراسی چوراسی پچیاسی چھیاسی
سٹیاسی ستیاسی اٹھیاسی نواسی نوے
اکانوے بانوے ترانوے چورانوے پچانوے چھیانوے ستانوے اٹھانوے ننانوے
سو ہزار لاکھ کروڑ ارب کھرب
""".split()
)

# Source https://www.google.com/intl/ur/inputtools/try/
_ordinal_words = set(
    """
پہلا پہلی پہلے دوسرا دوسری دوسرے تیسرا تیسری تیسرے
چوتھا چوتھی چوتھے پانچواں چھٹا چھٹی ساتواں آٹھواں نواں نویں
دسواں گیارہواں بارہواں تیرھواں چودھواں
پندرھواں سولہواں سترھواں اٹھارواں انیسواں بسیواں
""".split()
)
# fmt: on

_ORDINAL_SUFFIXES = ("واں", "ویں")
_SIGN_PREFIXES = ("+", "-", "±", "~", "−")
# Numeric grouping/decimal only. U+060C (،) is a list/clause comma and is not
# stripped. ASCII comma/period match spacy.lang.lex_attrs.like_num; U+066B and
# U+066C are the Arabic decimal and thousands separators.
_NUM_SEPARATORS = (",", ".", "٫", "٬")


def _strip_separators(text):
    for sep in _NUM_SEPARATORS:
        text = text.replace(sep, "")
    return text


def like_num(text):
    """Return whether text looks like a number, independent of sentence context."""
    if text.startswith(_SIGN_PREFIXES):
        text = text[1:]
    stripped = _strip_separators(text)
    if stripped.isdigit():
        return True
    if text.count("/") == 1:
        num, denom = text.split("/")
        if _strip_separators(num).isdigit() and _strip_separators(denom).isdigit():
            return True
    if text in _num_words or text in _ordinal_words:
        return True
    for suffix in _ORDINAL_SUFFIXES:
        if len(text) > len(suffix) and text.endswith(suffix):
            if text[: -len(suffix)] in _num_words:
                return True
    return False


LEX_ATTRS = {LIKE_NUM: like_num}

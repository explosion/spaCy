from ...attrs import LIKE_NUM

# Source https://quizlet.com/4271889/1-100-urdu-number-wordsurdu-numerals-flash-cards/
# http://www.urduword.com/lessons.php?lesson=numbers
# https://en.wikibooks.org/wiki/Urdu/Vocabulary/Numbers
# https://www.urdu-english.com/lessons/beginner/numbers

_num_words = """ایک دو تین چار پانچ چھ سات آٹھ نو دس گیارہ بارہ تیرہ چودہ پندرہ سولہ سترہ
 اٹهارا انیس بیس اکیس بائیس تئیس چوبیس پچیس چھببیس
ستایس اٹھائس انتيس تیس اکتیس بتیس تینتیس چونتیس پینتیس
 چھتیس سینتیس ارتیس انتالیس چالیس اکتالیس بیالیس تیتالیس
چوالیس پیتالیس چھیالیس سینتالیس اڑتالیس انچالیس پچاس اکاون باون
 تریپن چون پچپن چھپن ستاون اٹھاون انسٹھ ساثھ
اکسٹھ باسٹھ تریسٹھ چوسٹھ پیسٹھ چھیاسٹھ سڑسٹھ اڑسٹھ
انھتر ستر اکھتر بھتتر تیھتر چوھتر تچھتر چھیتر ستتر
اٹھتر انیاسی اسی اکیاسی بیاسی تیراسی چوراسی پچیاسی چھیاسی
 سٹیاسی اٹھیاسی نواسی نوے اکانوے بانوے ترانوے
چورانوے پچانوے چھیانوے ستانوے اٹھانوے ننانوے سو
""".split()

# source https://www.google.com/intl/ur/inputtools/try/

_ordinal_words = """پہلا دوسرا تیسرا چوتھا پانچواں چھٹا ساتواں آٹھواں نواں دسواں گیارہواں بارہواں تیرھواں چودھواں
 پندرھواں سولہواں سترھواں اٹھارواں انیسواں بسیواں
""".split()


def like_num(text):
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

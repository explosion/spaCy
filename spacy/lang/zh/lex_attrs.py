import re

from ...attrs import LIKE_NUM

_single_num_words = [
    "〇",
    "一",
    "二",
    "三",
    "四",
    "五",
    "六",
    "七",
    "八",
    "九",
    "十",
    "十一",
    "十二",
    "十三",
    "十四",
    "十五",
    "十六",
    "十七",
    "十八",
    "十九",
    "廿",
    "卅",
    "卌",
    "皕",
    "零",
    "壹",
    "贰",
    "叁",
    "肆",
    "伍",
    "陆",
    "柒",
    "捌",
    "玖",
    "拾",
    "拾壹",
    "拾贰",
    "拾叁",
    "拾肆",
    "拾伍",
    "拾陆",
    "拾柒",
    "拾捌",
    "拾玖",
]

_count_num_words = [
    "一",
    "二",
    "三",
    "四",
    "五",
    "六",
    "七",
    "八",
    "九",
    "壹",
    "贰",
    "叁",
    "肆",
    "伍",
    "陆",
    "柒",
    "捌",
    "玖",
]

_base_num_words = ["十", "百", "千", "万", "亿", "兆", "拾", "佰", "仟"]


def like_num(text):
    if text.startswith(("+", "-", "±", "~")):
        text = text[1:]
    text = text.replace(",", "").replace(".", "").replace("，", "").replace("。", "")
    if text.isdigit():
        return True
    if text.count("/") == 1:
        num, denom = text.split("/")
        if num.isdigit() and denom.isdigit():
            return True
    if text in _single_num_words:
        return True
    # fmt: off
    if re.match('^((' + '|'.join(_count_num_words) + '){1}'
                + '(' + '|'.join(_base_num_words) + '){1})+'
                + '(' + '|'.join(_count_num_words) + ')?$', text):
        return True
    # fmt: on
    return False


LEX_ATTRS = {LIKE_NUM: like_num}

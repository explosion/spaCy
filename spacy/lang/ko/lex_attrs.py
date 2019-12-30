from ...attrs import LIKE_NUM


_num_words = [
    "영",
    "공",
    # Native Korean number system
    "하나",
    "둘",
    "셋",
    "넷",
    "다섯",
    "여섯",
    "일곱",
    "여덟",
    "아홉",
    "열",
    "스물",
    "서른",
    "마흔",
    "쉰",
    "예순",
    "일흔",
    "여든",
    "아흔",
    # Sino-Korean number system
    "일",
    "이",
    "삼",
    "사",
    "오",
    "육",
    "칠",
    "팔",
    "구",
    "십",
    "백",
    "천",
    "만",
    "십만",
    "백만",
    "천만",
    "일억",
    "십억",
    "백억",
]


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
    if any(char.lower() in _num_words for char in text):
        return True
    return False


LEX_ATTRS = {LIKE_NUM: like_num}

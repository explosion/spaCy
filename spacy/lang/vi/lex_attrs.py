from ...attrs import LIKE_NUM


_num_words = [
    "không",  # Zero
    "một",  # One
    "mốt",  # Also one, irreplacable in niché cases for unit digit such as "51"="năm mươi mốt"
    "hai",  # Two
    "ba",  # Three
    "bốn",  # Four
    "tư",  # Also four, used in certain cases for unit digit such as "54"="năm mươi tư"
    "năm",  # Five
    "lăm",  # Also five, irreplacable in niché cases for unit digit such as "55"="năm mươi lăm"
    "sáu",  # Six
    "bảy",  # Seven
    "bẩy",  # Also seven, old fashioned
    "tám",  # Eight
    "chín",  # Nine
    "mười",  # Ten
    "chục",  # Also ten, used for counting in tens such as "20 eggs"="hai chục trứng"
    "trăm",  # Hundred
    "nghìn",  # Thousand
    "ngàn",  # Also thousand, used in the south
    "vạn",  # Ten thousand
    "triệu",  # Million
    "tỷ",  # Billion
    "tỉ",  # Also billion, used in combinatorics such as "tỉ_phú"="billionaire"
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
    if text.lower() in _num_words:
        return True
    return False


LEX_ATTRS = {LIKE_NUM: like_num}

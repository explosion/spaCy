from ...attrs import LIKE_NUM

# reference 1: https://en.wikipedia.org/wiki/Tibetan_numerals

_num_words = [
    "ཀླད་ཀོར་",
    "གཅིག་",
    "གཉིས་",
    "གསུམ་",
    "བཞི་",
    "ལྔ་",
    "དྲུག་",
    "བདུན་",
    "བརྒྱད་",
    "དགུ་",
    "བཅུ་",
    "བཅུ་གཅིག་",
    "བཅུ་གཉིས་",
    "བཅུ་གསུམ་",
    "བཅུ་བཞི་",
    "བཅུ་ལྔ་",
    "བཅུ་དྲུག་",
    "བཅུ་བདུན་",
    "བཅུ་པརྒྱད",
    "བཅུ་དགུ་",
    "ཉི་ཤུ་",
    "སུམ་ཅུ",
    "བཞི་བཅུ",
    "ལྔ་བཅུ",
    "དྲུག་ཅུ",
    "བདུན་ཅུ",
    "བརྒྱད་ཅུ",
    "དགུ་བཅུ",
    "བརྒྱ་",
    "སྟོང་",
    "ཁྲི་",
    "ས་ཡ་",
    "	བྱེ་བ་",
    "དུང་ཕྱུར་",
    "ཐེར་འབུམ་",
    "ཐེར་འབུམ་ཆེན་པོ་",
    "ཁྲག་ཁྲིག་",
    "ཁྲག་ཁྲིག་ཆེན་པོ་",
]


def like_num(text):
    """
    Check if text resembles a number
    """
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
    return False


LEX_ATTRS = {LIKE_NUM: like_num}

from ...attrs import LIKE_NUM

_num_words = [
    "ศูนย์",
    "หนึ่ง",
    "สอง",
    "สาม",
    "สี่",
    "ห้า",
    "หก",
    "เจ็ด",
    "แปด",
    "เก้า",
    "สิบ",
    "สิบเอ็ด",
    "ยี่สิบ",
    "ยี่สิบเอ็ด",
    "สามสิบ",
    "สามสิบเอ็ด",
    "สี่สิบ",
    "สี่สิบเอ็ด",
    "ห้าสิบ",
    "ห้าสิบเอ็ด",
    "หกสิบเอ็ด",
    "เจ็ดสิบ",
    "เจ็ดสิบเอ็ด",
    "แปดสิบ",
    "แปดสิบเอ็ด",
    "เก้าสิบ",
    "เก้าสิบเอ็ด",
    "ร้อย",
    "พัน",
    "ล้าน",
    "พันล้าน",
    "หมื่นล้าน",
    "แสนล้าน",
    "ล้านล้าน",
    "ล้านล้านล้าน",
    "ล้านล้านล้านล้าน",
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
    if text in _num_words:
        return True
    return False


LEX_ATTRS = {LIKE_NUM: like_num}

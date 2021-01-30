from ...attrs import LIKE_NUM

_num_words = [
    "సున్నా",
    "శూన్యం",
    "ఒకటి",
    "రెండు",
    "మూడు",
    "నాలుగు",
    "ఐదు",
    "ఆరు",
    "ఏడు",
    "ఎనిమిది",
    "తొమ్మిది",
    "పది",
    "పదకొండు",
    "పన్నెండు",
    "పదమూడు",
    "పద్నాలుగు",
    "పదిహేను",
    "పదహారు",
    "పదిహేడు",
    "పద్దెనిమిది",
    "పందొమ్మిది",
    "ఇరవై",
    "ముప్పై",
    "నలభై",
    "యాభై",
    "అరవై",
    "డెబ్బై",
    "ఎనభై",
    "తొంబై",
    "వంద",
    "నూరు",
    "వెయ్యి",
    "లక్ష",
    "కోటి",
]


def like_num(text):
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

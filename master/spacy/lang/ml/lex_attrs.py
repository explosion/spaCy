from ...attrs import LIKE_NUM


# reference 2: https://www.omniglot.com/language/numbers/malayalam.htm

_num_words = [
    "പൂജ്യം ",
    "ഒന്ന് ",
    "രണ്ട് ",
    "മൂന്ന് ",
    "നാല്‌ ",
    "അഞ്ച് ",
    "ആറ് ",
    "ഏഴ് ",
    "എട്ട് ",
    "ഒന്‍പത് ",
    "പത്ത് ",
    "പതിനൊന്ന്",
    "പന്ത്രണ്ട്",
    "പതി മൂന്നു",
    "പതിനാല്",
    "പതിനഞ്ച്",
    "പതിനാറ്",
    "പതിനേഴ്",
    "പതിനെട്ട്",
    "പത്തൊമ്പതു",
    "ഇരുപത്",
    "ഇരുപത്തിഒന്ന്",
    "ഇരുപത്തിരണ്ട്‌",
    "ഇരുപത്തിമൂന്ന്",
    "ഇരുപത്തിനാല്",
    "ഇരുപത്തിഅഞ്ചു",
    "ഇരുപത്തിആറ്",
    "ഇരുപത്തിഏഴ്",
    "ഇരുപത്തിഎട്ടു",
    "ഇരുപത്തിഒന്‍പത്",
    "മുപ്പത്",
    "മുപ്പത്തിഒന്ന്",
    "മുപ്പത്തിരണ്ട്",
    "മുപ്പത്തിമൂന്ന്",
    "മുപ്പത്തിനാല്",
    "മുപ്പത്തിഅഞ്ചു",
    "മുപ്പത്തിആറ്",
    "മുപ്പത്തിഏഴ്",
    "മുപ്പത്തിഎട്ട്",
    "മുപ്പത്തിഒന്‍പതു",
    "നാല്‍പത്‌ ",
    "അന്‍പത് ",
    "അറുപത് ",
    "എഴുപത് ",
    "എണ്‍പത് ",
    "തൊണ്ണൂറ് ",
    "നുറ് ",
    "ആയിരം ",
    "പത്തുലക്ഷം",
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

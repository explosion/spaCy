from ...attrs import LIKE_NUM
import re

# cf. Goyvaerts/Levithan 2009; case-insensitive, allow 4
roman_numerals_compile = re.compile(
    r"(?i)^(?=[MDCLXVI])M*(C[MD]|D?C{0,4})(X[CL]|L?X{0,4})(I[XV]|V?I{0,4})$"
)

_num_words = set(
    """
unus una unum duo duae tres tria quattuor quinque sex septem octo novem decem
""".split()
)

_ordinal_words = set(
    """
primus prima primum secundus secunda secundum tertius tertia tertium
""".split()
)


def like_num(text):
    if text.isdigit():
        return True
    if roman_numerals_compile.match(text):
        return True
    if text.lower() in _num_words:
        return True
    if text.lower() in _ordinal_words:
        return True
    return False


LEX_ATTRS = {LIKE_NUM: like_num}

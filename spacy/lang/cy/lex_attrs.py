from typing import Any, Callable, Dict

from ...attrs import LIKE_NUM

# Number words with their soft, nasal and aspirate mutations.
# fmt: off
_num_words = {
    "sero",
    "un",
    "dau", "ddau", "nau", "dwy", "ddwy", "nwy",
    "tri", "dri", "thri", "tair", "dair", "thair",
    "pedwar", "bedwar", "phedwar", "pedair", "bedair", "phedair",
    "pump", "bump", "phump", "pum", "bum", "phum",
    "chwech", "chwe",
    "saith",
    "wyth",
    "naw",
    "deg", "ddeg", "deng", "ddeng",
    "deuddeg", "ddeuddeg", "deuddeng", "ddeuddeng",
    "pymtheg", "bymtheg", "phymtheg", "pymtheng", "bymtheng", "phymtheng",
    "deunaw", "ddeunaw", "neunaw",
    "ugain", "hugain",
    "deugain", "ddeugain", "neugain",
    "trigain", "drigain", "thrigain",
    "cant", "gant", "chant", "can", "gan", "chan",
    "mil", "fil",
    "miliwn", "filiwn",
    "biliwn",
    "triliwn", "driliwn", "thriliwn",
    "cwadriliwn", "gwadriliwn", "chwadriliwn",
}
# fmt: on


def like_num(text: str) -> bool:
    if text.startswith(("+", "-", "±", "~")):
        text = text[1:]
    text = text.replace(",", "").replace(".", "")
    if text.isdigit():
        return True
    if text.count("/") == 1:
        num, denom = text.split("/")
        if num.isdigit() and denom.isdigit():
            return True
    return text.lower() in _num_words


LEX_ATTRS: Dict[int, Callable[[str], Any]] = {LIKE_NUM: like_num}

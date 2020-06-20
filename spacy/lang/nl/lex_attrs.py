from ...attrs import LIKE_NUM


_num_words = set(
    """
nul een één twee drie vier vijf zes zeven acht negen tien elf twaalf dertien
veertien twintig dertig veertig vijftig zestig zeventig tachtig negentig honderd
duizend miljoen miljard biljoen biljard triljoen triljard
""".split()
)

_ordinal_words = set(
    """
eerste tweede derde vierde vijfde zesde zevende achtste negende tiende elfde
twaalfde dertiende veertiende twintigste dertigste veertigste vijftigste
zestigste zeventigste tachtigste negentigste honderdste duizendste miljoenste
miljardste biljoenste biljardste triljoenste triljardste
""".split()
)


def like_num(text):
    # This only does the most basic check for whether a token is a digit
    # or matches one of the number words. In order to handle numbers like
    # "drieëntwintig", more work is required.
    # See this discussion: https://github.com/explosion/spaCy/pull/1177
    text = text.replace(",", "").replace(".", "")
    if text.isdigit():
        return True
    if text.count("/") == 1:
        num, denom = text.split("/")
        if num.isdigit() and denom.isdigit():
            return True
    if text.lower() in _num_words:
        return True
    if text.lower() in _ordinal_words:
        return True
    return False


LEX_ATTRS = {LIKE_NUM: like_num}

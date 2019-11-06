# coding: utf8
from __future__ import unicode_literals

from ...attrs import LIKE_NUM


_num_words = set(
    """
null eent zwee dräi véier fënnef sechs ziwen aacht néng zéng eelef zwielef dräizéng
véierzéng foffzéng siechzéng siwwenzéng uechtzeng uechzeng nonnzéng nongzéng zwanzeg drësseg véierzeg foffzeg sechzeg siechzeg siwenzeg achtzeg achzeg uechtzeg uechzeg nonnzeg
honnert dausend millioun milliard billioun billiard trillioun triliard
""".split()
)

_ordinal_words = set(
    """
éischten zweeten drëtten véierten fënneften sechsten siwenten aachten néngten zéngten eeleften
zwieleften dräizéngten véierzéngten foffzéngten siechzéngten uechtzéngen uechzéngten nonnzéngten nongzéngten zwanzegsten
drëssegsten véierzegsten foffzegsten siechzegsten siwenzegsten uechzegsten nonnzegsten
honnertsten dausendsten milliounsten
milliardsten billiounsten billiardsten trilliounsten trilliardsten
""".split()
)


def like_num(text):
    """
    check if text resembles a number
    """
    text = text.replace(",", "").replace(".", "")
    if text.isdigit():
        return True
    if text.count("/") == 1:
        num, denom = text.split("/")
        if num.isdigit() and denom.isdigit():
            return True
    if text in _num_words:
        return True
    if text in _ordinal_words:
        return True
    return False


LEX_ATTRS = {LIKE_NUM: like_num}

import re

from ...attrs import LIKE_NUM

# cf. Goyvaerts/Levithan 2009; case-insensitive, allow 4
roman_numerals_compile = re.compile(
    r"(?i)^(?=[MDCLXVI])M*(C[MD]|D?C{0,4})(X[CL]|L?X{0,4})(I[XV]|V?I{0,4})$"
)

_num_words = """unus una unum duo duae tres tria quattuor quinque sex septem octo novem decem undecim duodecim tredecim quattuordecim quindecim sedecim septendecim duodeviginti undeviginti viginti triginta quadraginta quinquaginta sexaginta septuaginta octoginta nonaginta centum ducenti ducentae ducenta trecenti trecentae trecenta quadringenti quadringentae quadringenta quingenti quingentae quingenta sescenti sescentae sescenta septingenti septingentae septingenta octingenti octingentae octingenta nongenti nongentae nongenta mille
""".split()

_num_words += [item.replace("v", "u") for item in _num_words]
_num_words = set(_num_words)

_ordinal_words = """primus prima primum secundus secunda secundum tertius tertia tertium quartus quarta quartum quintus quinta quintum sextus sexta sextum septimus septima septimum octavus octava octavum nonus nona nonum decimus decima decimum undecimus undecima undecimum duodecimus duodecima duodecimum duodevicesimus duodevicesima duodevicesimum undevicesimus undevicesima undevicesimum vicesimus vicesima vicesimum tricesimus tricesima tricesimum quadragesimus quadragesima quadragesimum quinquagesimus quinquagesima quinquagesimum sexagesimus sexagesima sexagesimum septuagesimus septuagesima septuagesimum octogesimus octogesima octogesimum nonagesimus nonagesima nonagesimum centesimus centesima centesimum ducentesimus ducentesima ducentesimum trecentesimus trecentesima trecentesimum quadringentesimus quadringentesima quadringentesimum quingentesimus quingentesima quingentesimum sescentesimus sescentesima sescentesimum septingentesimus septingentesima septingentesimum octingentesimus octingentesima octingentesimum nongentesimus nongentesima nongentesimum millesimus millesima millesimum""".split()

_ordinal_words += [item.replace("v", "u") for item in _ordinal_words]
_ordinal_words = set(_ordinal_words)


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

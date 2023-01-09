from ...attrs import LIKE_NUM

_num_words = [
    "nnooti",  # Zero
    "zeero",  # zero
    "emu",  # one
    "bbiri",  # two
    "ssatu",  # three
    "nnya",  # four
    "ttaano",  # five
    "mukaaga",  # six
    "musanvu",  # seven
    "munaana",  # eight
    "mwenda",  # nine
    "kkumi",  # ten
    "kkumi n'emu",  # eleven
    "kkumi na bbiri",  # twelve
    "kkumi na ssatu",  # thirteen
    "kkumi na nnya",  # forteen
    "kkumi na ttaano",  # fifteen
    "kkumi na mukaaga",  # sixteen
    "kkumi na musanvu",  # seventeen
    "kkumi na munaana",  # eighteen
    "kkumi na mwenda",  # nineteen
    "amakumi abiri",  # twenty
    "amakumi asatu",  # thirty
    "amakumi ana",  # forty
    "amakumi ataano",  # fifty
    "nkaaga",  # sixty
    "nsanvu",  # seventy
    "kinaana",  # eighty
    "kyenda",  # ninety
    "kikumi",  # hundred
    "lukumi",  # thousand
    "kakadde",  # million
    "kawumbi",  # billion
    "kase",  # trillion
    "katabalika",  # quadrillion
    "keesedde",  # gajillion
    "kafukunya",  # bazillion
    "ekisooka",  # first
    "ekyokubiri",  # second
    "ekyokusatu",  # third
    "ekyokuna",  # fourth
    "ekyokutaano",  # fifith
    "ekyomukaaga",  # sixth
    "ekyomusanvu",  # seventh
    "eky'omunaana",  # eighth
    "ekyomwenda",  # nineth
    "ekyekkumi",  # tenth
    "ekyekkumi n'ekimu",  # eleventh
    "ekyekkumi n'ebibiri",  # twelveth
    "ekyekkumi n'ebisatu",  # thirteenth
    "ekyekkumi n'ebina",  # fourteenth
    "ekyekkumi n'ebitaano",  # fifteenth
    "ekyekkumi n'omukaaga",  # sixteenth
    "ekyekkumi n'omusanvu",  # seventeenth
    "ekyekkumi n'omunaana",  # eigteenth
    "ekyekkumi n'omwenda",  # nineteenth
    "ekyamakumi abiri",  # twentieth
    "ekyamakumi asatu",  # thirtieth
    "ekyamakumi ana",  # fortieth
    "ekyamakumi ataano",  # fiftieth
    "ekyenkaaga",  # sixtieth
    "ekyensanvu",  # seventieth
    "ekyekinaana",  # eightieth
    "ekyekyenda",  # ninetieth
    "ekyekikumi",  # hundredth
    "ekyolukumi",  # thousandth
    "ekyakakadde",  # millionth
    "ekyakawumbi",  # billionth
    "ekyakase",  # trillionth
    "ekyakatabalika",  # quadrillionth
    "ekyakeesedde",  # gajillionth
    "ekyakafukunya",  # bazillionth
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
    text_lower = text.lower()
    if text_lower in _num_words:
        return True
    return False


LEX_ATTRS = {LIKE_NUM: like_num}

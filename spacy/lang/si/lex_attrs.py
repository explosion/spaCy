from ...attrs import LIKE_NUM

_num_words = [
    "බින්දුව",
    "බිංදුව","එක","දෙක","තුන","හතර","පහ","හය","හත","අට","නවය","නමය","දහය",
    "එකොළහ","දොළහ","දහතුන","දහහතර","දාහතර","පහළව","පහළොව","දහසය","දහහත","දාහත","දහඅට","දහනවය",
    "විස්ස","තිහ","හතළිහ","පනහ","හැට","හැත්තෑව","අසූව","අනූව","සියය","සියවෙනි"
    "දහස","දාහ","ලක්ෂය","මිලියනය","කෝටිය","බිලියනය","ට්‍රිලියනය",
    ]

_ordinal_words = [
    "පළමු",        # first
    "දෙවන",        # second
    "තෙවන","තුන්වන",        # third
    "සතරවන",       # fourth
    "පස්වන",       # fifth
    "හයවන",        # sixth
    "හත්වන",       # seventh
    "අටවන",        # eighth
    "නවවන",        # ninth
    "දහවන",        # tenth
    "එකොළොස්වන",   # eleventh
    "දොළොස්වන",    # twelfth
    "දහතුන්වන",    # thirteenth
    "දහහතරවන",     # fourteenth
    "පහලොස්වන",     # fifteenth
    "දහසයවන",      # sixteenth
    "දහහත්වන",     # seventeenth
    "දහඅටවන",      # eighteenth
    "දහනවවන",      # nineteenth
    "විසිවන",       # twentieth
    "තිස්වන",       # thirtieth
    "හතළිස්වන",    # fortieth
    "පනස්වන",      # fiftieth
    "හැටවන",       # sixtieth
    "හැත්තෑවන",    # seventieth
    "අසූවන",       # eightieth
    "අනූවන",       # ninetieth
    "සියවන",       # hundredth
    "දහස්වන",      # thousandth
    "මිලියනවන",   # millionth
    "බිලියනවන",   # billionth
    "ට්‍රිලියනවන",    # trillionth
    "ක්වාඩ්‍රිලියන්වන", # quadrillionth
    "ක්වින්ටිලියන්වන",  # quintillionth
    "සෙක්ස්ටිලියන්වන",  # sextillionth
    "සෙප්ටිලියන්වන",    # septillionth
    "ඔක්ටිලියන්වන",     # octillionth
    "නොනිලියන්වන",      # nonillionth
    "ඩෙසිලියන්වන",      # decillionth
    "ගජිලියන්වන",       # gajillionth  (informal/made-up)
    "බසිලියන්වන",       # bazillionth  (informal/made-up)
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
    # Sinhala ordinal suffix check — no .lower() needed
    if text in _ordinal_words:
        return True
    # "23 වෙනි" / "100 වන" — with space
    parts = text.split()
    if len(parts) == 2 and parts[0].isdigit() and parts[1] in ("වන", "වෙනි"):
        return True
    # "තුන්වන", "සියවන" — suffix attached
    if text.endswith("වෙනි"):
        stem = text[:-4]
        if stem.isdigit() or stem in _num_words:
            return True
    if text.endswith("වන"):
        stem = text[:-2]
        if stem.isdigit() or stem in _num_words:
            return True
    return False



LEX_ATTRS = {LIKE_NUM: like_num}

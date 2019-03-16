# coding: utf8
from __future__ import unicode_literals

split_chars = lambda char: list(char.strip().split(" "))
merge_chars = lambda char: char.strip().replace(" ", "|")
group_chars = lambda char: char.strip().replace(" ", "")

_bengali = r"\u0980-\u09FF"

_hebrew = r"\u0591-\u05F4\uFB1D-\uFB4F"

# Latin standard
_latin_u_standard = r"A-Z"
_latin_l_standard = r"a-z"
_latin_standard = _latin_u_standard + _latin_l_standard

_latin_u_standard_fullwidth = r"\uFF21-\uFF3A"
_latin_l_standard_fullwidth = r"\uFF41-\uFF5A"
_latin_standard_fullwidth = _latin_u_standard_fullwidth + _latin_l_standard_fullwidth

# letters with diacritics - French, German, Icelandic, Spanish
_latin_u_supplement = r"\u00C0-\u00D6\u00D8-\u00DE"
_latin_l_supplement = r"\u00DF-\u00F6\u00F8-\u00FF"
_latin_supplement = r"\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u00FF"

# letters with diacritics - Catalan, Czech, Latin, Latvian, Lithuanian, Polish, Slovak, Turkish, Welsh
_latin_u_extendedA = (
    r"\u0100\u0102\u0104\u0106\u0108\u010A\u010C\u010E\u0110\u0112\u0114\u0116\u0118\u011A\u011C"
    r"\u011E\u0120\u0122\u0124\u0126\u0128\u012A\u012C\u012E\u0130\u0132\u0134\u0136\u0139\u013B"
    r"\u013D\u013F\u0141\u0143\u0145\u0147\u014A\u014C\u014E\u0150\u0152\u0154\u0156\u0158"
    r"\u015A\u015C\u015E\u0160\u0162\u0164\u0166\u0168\u016A\u016C\u016E\u0170\u0172\u0174\u0176"
    r"\u0178\u0179\u017B\u017D"
)
_latin_l_extendedA = (
    r"\u0101\u0103\u0105\u0107\u0109\u010B\u010D\u010F\u0111\u0113\u0115\u0117\u0119\u011B\u011D"
    r"\u011F\u0121\u0123\u0125\u0127\u0129\u012B\u012D\u012F\u0131\u0133\u0135\u0137\u0138\u013A"
    r"\u013C\u013E\u0140\u0142\u0144\u0146\u0148\u0149\u014B\u014D\u014F\u0151\u0153\u0155\u0157"
    r"\u0159\u015B\u015D\u015F\u0161\u0163\u0165\u0167\u0169\u016B\u016D\u016F\u0171\u0173\u0175"
    r"\u0177\u017A\u017C\u017E\u017F"
)
_latin_extendedA = r"\u0100-\u017F"

# special characters - Khoisan, Pan-Nigerian, Pinyin, Romanian
# those that are a combination of both upper and lower letters are only included in the group _latin_extendedB
_latin_u_extendedB = (
    r"\u0181\u0182\u0184\u0186\u0187\u0189-\u018B\u018E-\u0191\u0193\u0194\u0196-\u0198\u019C"
    r"\u019D\u019F\u01A0\u01A2\u01A4\u01A6\u01A7\u01A9\u01AC\u01AE\u01AF\u01B1-\u01B3\u01B5"
    r"\u01B7\u01B8\u01BC\u01C4\u01C7\u01CA\u01CD\u01CF\u01D1\u01D3\u01D5\u01D7\u01D9\u01DB"
    r"\u01DE\u01E0\u01E2\u01E4\u01E6\u01E8\u01EA\u01EC\u01EE\u01F1\u01F4\u01F6-\u01F8\u01FA"
    r"\u01FC\u01FE\u0200\u0202\u0204\u0206\u0208\u020A\u020C\u020E\u0210\u0212\u0214\u0216"
    r"\u0218\u021A\u021C\u021E\u0220\u0222\u0224\u0226\u0228\u022A\u022C\u022E\u0230\u0232"
    r"\u023A\u023B\u023D\u023E\u0241\u0243-\u0246\u0248\u024A\u024C\u024E"
)
_latin_l_extendedB = (
    r"\u0180\u0183\u0185\u0188\u018C\u018D\u0192\u0195\u0199-\u019B\u019E\u01A1\u01A3\u01A5"
    r"\u01A8\u01AA\u01AB\u01AD\u01B0\u01B4\u01B6\u01B9\u01BA\u01BD-\u01BF\u01C6\u01C9\u01CC"
    r"\u01CE\u01D0\u01D2\u01D4\u01D6\u01D8\u01DA\u01DC\u01DD\u01DF\u01E1\u01E3\u01E5\u01E7"
    r"\u01E9\u01EB\u01ED\u01EF\u01F0\u01F3\u01F5\u01F9\u01FB\u01FD\u01FF\u0201\u0203\u0205"
    r"\u0207\u0209\u020B\u020D\u020F\u0211\u0213\u0215\u0217\u0219\u021B\u021D\u021F\u0221"
    r"\u0223\u0225\u0227\u0229\u022B\u022D\u022F\u0231\u0233-\u0239\u023C\u023F\u0240\u0242"
    r"\u0247\u0249\u024B\u024D\u024F"
)
_latin_extendedB = r"\u0180-\u01BF\u01C4-\u024F"

# special characters - Uighur, Uralic Phonetic
_latin_u_extendedC = (
    r"\u2C60\u2C62-\u2C64\u2C67\u2C69\u2C6B\u2C6D-\u2C70\u2C72\u2C75\u2C7E\u2C7F"
)
_latin_l_extendedC = (
    r"\u2C61\u2C65\u2C66\u2C68\u2C6A\u2C6C\u2C71\u2C73\u2C74\u2C76-\u2C7B"
)
_latin_extendedC = r"\u2C60-\u2C7B\u2C7E\u2C7F"

# special characters - phonetic, Mayan, Medieval
_latin_u_extendedD = (
    r"\uA722\uA724\uA726\uA728\uA72A\uA72C\uA72E\uA732\uA734\uA736\uA738\uA73A\uA73C"
    r"\uA73E\uA740\uA742\uA744\uA746\uA748\uA74A\uA74C\uA74E\uA750\uA752\uA754\uA756\uA758"
    r"\uA75A\uA75C\uA75E\uA760\uA762\uA764\uA766\uA768\uA76A\uA76C\uA76E\uA779\uA77B\uA77D"
    r"\uA77E\uA780\uA782\uA784\uA786\uA78B\uA78D\uA790\uA792\uA796\uA798\uA79A\uA79C\uA79E"
    r"\uA7A0\uA7A2\uA7A4\uA7A6\uA7A8\uA7AA-\uA7AE\uA7B0-\uA7B4\uA7B6\uA7B8"
)
_latin_l_extendedD = (
    r"\uA723\uA725\uA727\uA729\uA72B\uA72D\uA72F-\uA731\uA733\uA735\uA737\uA739\uA73B\uA73D"
    r"\uA73F\uA741\uA743\uA745\uA747\uA749\uA74B\uA74D\uA74F\uA751\uA753\uA755\uA757\uA759"
    r"\uA75B\uA75D\uA75F\uA761\uA763\uA765\uA767\uA769\uA76B\uA76D\uA76F\uA771-\uA778\uA77A"
    r"\uA77C\uA77F\uA781\uA783\uA785\uA787\uA78C\uA78E\uA791\uA793-\uA795\uA797\uA799\uA79B"
    r"\uA79D\uA79F\uA7A1\uA7A3\uA7A5\uA7A7\uA7A9\uA7AF\uA7B5\uA7B7\uA7B9\uA7FA"
)
_latin_extendedD = r"\uA722-\uA76F\uA771-\uA787\uA78B-\uA78E\uA790-\uA7B9\uA7FA"

# special characters - phonetic Teuthonista and Sakha
_latin_l_extendedE = r"\uAB30-\uAB5A\uAB60-\uAB64"
_latin_extendedE = _latin_l_extendedE

# phonetic letters - Greek, Latin, Cyrillic
_latin_l_phonetic = r"\u0250-\u02AF\u1D00-\u1D25\u1D6B-\u1D77\u1D79-\u1D9A"
_latin_phonetic = _latin_l_phonetic

# letters with multiple diacritics - Vietnamese
_latin_u_diacritics = (
    r"\u1E00\u1E02\u1E04\u1E06\u1E08\u1E0A\u1E0C\u1E0E\u1E10\u1E12\u1E14\u1E16\u1E18\u1E1A"
    r"\u1E1C\u1E1E\u1E20\u1E22\u1E24\u1E26\u1E28\u1E2A\u1E2C\u1E2E\u1E30\u1E32\u1E34\u1E36"
    r"\u1E38\u1E3A\u1E3C\u1E3E\u1E40\u1E42\u1E44\u1E46\u1E48\u1E4A\u1E4C\u1E4E\u1E50\u1E52"
    r"\u1E54\u1E56\u1E58\u1E5A\u1E5C\u1E5E\u1E60\u1E62\u1E64\u1E66\u1E68\u1E6A\u1E6C\u1E6E"
    r"\u1E70\u1E72\u1E74\u1E76\u1E78\u1E7A\u1E7C\u1E7E\u1E80\u1E82\u1E84\u1E86\u1E88\u1E8A"
    r"\u1E8C\u1E8E\u1E90\u1E92\u1E94\u1E9E\u1EA0\u1EA2\u1EA4\u1EA6\u1EA8\u1EAA\u1EAC\u1EAE"
    r"\u1EB0\u1EB2\u1EB4\u1EB6\u1EB8\u1EBA\u1EBC\u1EBE\u1EC0\u1EC2\u1EC4\u1EC6\u1EC8"
    r"\u1ECA\u1ECC\u1ECE\u1ED0\u1ED2\u1ED4\u1ED6\u1ED8\u1EDA\u1EDC\u1EDE\u1EE0\u1EE2\u1EE4"
    r"\u1EE6\u1EE8\u1EEA\u1EEC\u1EEE\u1EF0\u1EF2\u1EF4\u1EF6\u1EF8\u1EFA\u1EFC\u1EFE"
)
_latin_l_diacritics = (
    r"\u1E01\u1E03\u1E05\u1E07\u1E09\u1E0B\u1E0D\u1E0F\u1E11\u1E13\u1E15\u1E17\u1E19\u1E1B"
    r"\u1E1D\u1E1F\u1E21\u1E23\u1E25\u1E27\u1E29\u1E2B\u1E2D\u1E2F\u1E31\u1E33\u1E35\u1E37"
    r"\u1E39\u1E3B\u1E3D\u1E3F\u1E41\u1E43\u1E45\u1E47\u1E49\u1E4B\u1E4D\u1E4F\u1E51\u1E53"
    r"\u1E55\u1E57\u1E59\u1E5B\u1E5D\u1E5F\u1E61\u1E63\u1E65\u1E67\u1E69\u1E6B\u1E6D\u1E6F"
    r"\u1E71\u1E73\u1E75\u1E77\u1E79\u1E7B\u1E7D\u1E7F\u1E81\u1E83\u1E85\u1E87\u1E89\u1E8B"
    r"\u1E8D\u1E8F\u1E91\u1E93\u1E95-\u1E9D\u1E9F\u1EA1\u1EA3\u1EA5\u1EA7\u1EA9\u1EAB\u1EAD"
    r"\u1EAF\u1EB1\u1EB3\u1EB5\u1EB7\u1EB9\u1EBB\u1EBD\u1EBF\u1EC1\u1EC3\u1EC5\u1EC7\u1EC9"
    r"\u1ECB\u1ECD\u1ECF\u1ED1\u1ED3\u1ED5\u1ED7\u1ED9\u1EDB\u1EDD\u1EDF\u1EE1\u1EE3\u1EE5"
    r"\u1EE7\u1EE9\u1EEB\u1EED\u1EEF\u1EF1\u1EF3\u1EF5\u1EF7\u1EF9\u1EFB\u1EFD\u1EFF"
)
_latin_diacritics = r"\u1E00-\u1EFF"

# all lower latin classes
LATIN_LOWER_BASIC = (
    _latin_l_standard
    + _latin_l_standard_fullwidth
    + _latin_l_supplement
    + _latin_l_extendedA
)
LATIN_LOWER = (
    LATIN_LOWER_BASIC
    + _latin_l_extendedB
    + _latin_l_extendedC
    + _latin_l_extendedD
    + _latin_l_extendedE
    + _latin_l_phonetic
    + _latin_l_diacritics
)

# all upper latin classes
LATIN_UPPER_BASIC = (
    _latin_u_standard
    + _latin_u_standard_fullwidth
    + _latin_u_supplement
    + _latin_u_extendedA
)
LATIN_UPPER = (
    LATIN_UPPER_BASIC
    + _latin_u_extendedB
    + _latin_u_extendedC
    + _latin_u_extendedD
    + _latin_u_diacritics
)

# all latin classes
LATIN_BASIC = (
    _latin_standard + _latin_standard_fullwidth + _latin_supplement + _latin_extendedA
)
LATIN = (
    LATIN_BASIC
    + _latin_extendedB
    + _latin_extendedC
    + _latin_extendedD
    + _latin_extendedE
    + _latin_phonetic
    + _latin_diacritics
)

_persian = (
    r"\u0620-\u064A\u066E-\u06D5\u06E5-\u06FF\u0750-\u077F\u08A0-\u08BD"
    r"\uFB50-\uFBB1\uFBD3-\uFD3D\uFD50-\uFDC7\uFDF0-\uFDFB\uFE70-\uFEFC\U0001EE00-\U0001EEBB"
)

_russian_lower = r"ёа-я"
_russian_upper = r"ЁА-Я"
_russian = r"ёа-яЁА-Я"

_sinhala = r"\u0D85-\u0D96\u0D9A-\u0DB1\u0DB3-\u0DBB\u0DBD\u0DC0-\u0DC6"

_tatar_lower = r"әөүҗңһ"
_tatar_upper = r"ӘӨҮҖҢҺ"
_tatar = r"әөүҗңһӘӨҮҖҢҺ"

_greek_lower = r"α-ωάέίόώήύ"
_greek_upper = r"Α-ΩΆΈΊΌΏΉΎ"
_greek = r"α-ωάέίόώήύΑ-ΩΆΈΊΌΏΉΎ"

_ukrainian_lower = r"а-щюяіїєґ"
_ukrainian_upper = r"А-ЩЮЯІЇЄҐ"
_ukrainian = r"а-щюяіїєґА-ЩЮЯІЇЄҐ"

_upper = LATIN_UPPER + _russian_upper + _tatar_upper + _greek_upper + _ukrainian_upper
_lower = LATIN_LOWER + _russian_lower + _tatar_lower + _greek_lower + _ukrainian_lower

_uncased = _bengali + _hebrew + _persian + _sinhala

ALPHA = group_chars(LATIN + _russian + _tatar + _greek + _ukrainian + _uncased)
ALPHA_LOWER = group_chars(_lower + _uncased)
ALPHA_UPPER = group_chars(_upper + _uncased)

_units = (
    "km km² km³ m m² m³ dm dm² dm³ cm cm² cm³ mm mm² mm³ ha µm nm yd in ft "
    "kg g mg µg t lb oz m/s km/h kmh mph hPa Pa mbar mb MB kb KB gb GB tb "
    "TB T G M K % км км² км³ м м² м³ дм дм² дм³ см см² см³ мм мм² мм³ нм "
    "кг г мг м/с км/ч кПа Па мбар Кб КБ кб Мб МБ мб Гб ГБ гб Тб ТБ тб"
    "كم كم² كم³ م م² م³ سم سم² سم³ مم مم² مم³ كم غرام جرام جم كغ ملغ كوب اكواب"
)
_currency = r"\$ £ € ¥ ฿ US\$ C\$ A\$ ₽ ﷼ ₴"

# These expressions contain various unicode variations, including characters
# used in Chinese (see #1333, #1340, #1351) – unless there are cross-language
# conflicts, spaCy's base tokenizer should handle all of those by default
_punct = (
    r"… …… , : ; \! \? ¿ ؟ ¡ \( \) \[ \] \{ \} < > _ # \* & 。 ？ ！ ， 、 ； ： ～ · । ، ؛ ٪"
)
_quotes = r'\' " ” “ ` ‘ ´ ’ ‚ , „ » « 「 」 『 』 （ ） 〔 〕 【 】 《 》 〈 〉'
_hyphens = "- – — -- --- —— ~"

# Various symbols like dingbats, but also emoji
# Details: https://www.compart.com/en/unicode/category/So
_other_symbols = (
    r"\u00A6\u00A9\u00AE\u00B0\u0482\u058D\u058E\u060E\u060F\u06DE\u06E9\u06FD\u06FE\u07F6\u09FA\u0B70"
    r"\u0BF3-\u0BF8\u0BFA\u0C7F\u0D4F\u0D79\u0F01-\u0F03\u0F13\u0F15-\u0F17\u0F1A-\u0F1F\u0F34"
    r"\u0F36\u0F38\u0FBE-\u0FC5\u0FC7-\u0FCC\u0FCE\u0FCF\u0FD5-\u0FD8\u109E\u109F\u1390-\u1399"
    r"\u1940\u19DE-\u19FF\u1B61-\u1B6A\u1B74-\u1B7C\u2100\u2101\u2103-\u2106\u2108\u2109\u2114\u2116"
    r"\u2117\u211E-\u2123\u2125\u2127\u2129\u212E\u213A\u213B\u214A\u214C\u214D\u214F\u218A\u218B"
    r"\u2195-\u2199\u219C-\u219F\u21A1\u21A2\u21A4\u21A5\u21A7-\u21AD\u21AF-\u21CD\u21D0\u21D1\u21D3"
    r"\u21D5-\u21F3\u2300-\u2307\u230C-\u231F\u2322-\u2328\u232B-\u237B\u237D-\u239A\u23B4-\u23DB"
    r"\u23E2-\u2426\u2440-\u244A\u249C-\u24E9\u2500-\u25B6\u25B8-\u25C0\u25C2-\u25F7\u2600-\u266E"
    r"\u2670-\u2767\u2794-\u27BF\u2800-\u28FF\u2B00-\u2B2F\u2B45\u2B46\u2B4D-\u2B73\u2B76-\u2B95"
    r"\u2B98-\u2BC8\u2BCA-\u2BFE\u2CE5-\u2CEA\u2E80-\u2E99\u2E9B-\u2EF3\u2F00-\u2FD5\u2FF0-\u2FFB"
    r"\u3004\u3012\u3013\u3020\u3036\u3037\u303E\u303F\u3190\u3191\u3196-\u319F\u31C0-\u31E3"
    r"\u3200-\u321E\u322A-\u3247\u3250\u3260-\u327F\u328A-\u32B0\u32C0-\u32FE\u3300-\u33FF\u4DC0-\u4DFF"
    r"\uA490-\uA4C6\uA828-\uA82B\uA836\uA837\uA839\uAA77-\uAA79\uFDFD\uFFE4\uFFE8\uFFED\uFFEE\uFFFC"
    r"\uFFFD\U00010137-\U0001013F\U00010179-\U00010189\U0001018C-\U0001018E\U00010190-\U0001019B"
    r"\U000101A0\U000101D0-\U000101FC\U00010877\U00010878\U00010AC8\U0001173F\U00016B3C-\U00016B3F"
    r"\U00016B45\U0001BC9C\U0001D000-\U0001D0F5\U0001D100-\U0001D126\U0001D129-\U0001D164"
    r"\U0001D16A-\U0001D16C\U0001D183\U0001D184\U0001D18C-\U0001D1A9\U0001D1AE-\U0001D1E8"
    r"\U0001D200-\U0001D241\U0001D245\U0001D300-\U0001D356\U0001D800-\U0001D9FF\U0001DA37-\U0001DA3A"
    r"\U0001DA6D-\U0001DA74\U0001DA76-\U0001DA83\U0001DA85\U0001DA86\U0001ECAC\U0001F000-\U0001F02B"
    r"\U0001F030-\U0001F093\U0001F0A0-\U0001F0AE\U0001F0B1-\U0001F0BF\U0001F0C1-\U0001F0CF"
    r"\U0001F0D1-\U0001F0F5\U0001F110-\U0001F16B\U0001F170-\U0001F1AC\U0001F1E6-\U0001F202"
    r"\U0001F210-\U0001F23B\U0001F240-\U0001F248\U0001F250\U0001F251\U0001F260-\U0001F265"
    r"\U0001F300-\U0001F3FA\U0001F400-\U0001F6D4\U0001F6E0-\U0001F6EC\U0001F6F0-\U0001F6F9"
    r"\U0001F700-\U0001F773\U0001F780-\U0001F7D8\U0001F800-\U0001F80B\U0001F810-\U0001F847"
    r"\U0001F850-\U0001F859\U0001F860-\U0001F887\U0001F890-\U0001F8AD\U0001F900-\U0001F90B"
    r"\U0001F910-\U0001F93E\U0001F940-\U0001F970\U0001F973-\U0001F976\U0001F97A\U0001F97C-\U0001F9A2"
    r"\U0001F9B0-\U0001F9B9\U0001F9C0-\U0001F9C2\U0001F9D0-\U0001F9FF\U0001FA60-\U0001FA6D"
)

UNITS = merge_chars(_units)
CURRENCY = merge_chars(_currency)
PUNCT = merge_chars(_punct)
HYPHENS = merge_chars(_hyphens)
ICONS = _other_symbols

LIST_UNITS = split_chars(_units)
LIST_CURRENCY = split_chars(_currency)
LIST_QUOTES = split_chars(_quotes)
LIST_PUNCT = split_chars(_punct)
LIST_HYPHENS = split_chars(_hyphens)
LIST_ELLIPSES = [r"\.\.+", "…"]
LIST_ICONS = [r"[{i}]".format(i=_other_symbols)]

CONCAT_QUOTES = group_chars(_quotes)
CONCAT_ICONS = _other_symbols

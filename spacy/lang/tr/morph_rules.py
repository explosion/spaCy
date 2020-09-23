# coding: utf8
from __future__ import unicode_literals

from ...symbols import LEMMA, PRON_LEMMA

_adverbs = [
        "apansızın",
        "aslen",
        "aynen",
        "ayrıyeten",
        "basbayağı",
        "başaşağı",
        "belki",
        "çatkapı",
        "demin",
        "derhal",
        "doyasıya",
        "düpedüz",
        "ebediyen",
        "elbet",
        "elbette",
        "enikonu",
        "epey",
        "epeyce",
        "epeydir",
        "esasen",
        "evvela",
        "galiba",
        "gayet",
        "genellikle",
        "gerçekten",
        "gerisingeri",
        "giderayak",
        "gitgide",
        "gıyaben",
        "gözgöze",
        "güçbela",
        "gündüzleyin",
        "güya",
        "habire",
        "hakikaten",
        "hakkaten",
        "halen",
        "halihazırda",
        "harfiyen",
        "haricen",
        "hasbelkader",
        "hemen",
        "henüz",
        "hep",
        "hepten",
        "herhalde",
        "hiç",
        "hükmen",
        "ihtiyaten",
        "illaki",
"ismen",
        "iştiraken",
        "izafeten",
        "kalben",
        "kargatulumba",
        "kasten",
        "katiyen",
        "katiyyen",
        "kazara",
        "kefaleten",
        "kendiliğinden",
        "kerhen",
        "kesinkes",
        "kesinlikle",
        "keşke",
        "kimileyin",
        "külliyen",
        "layıkıyla",
        "maalesef",
        "mahsusçuktan",
        "masumane",
        "malulen",
        "mealen",
        "mecazen",
        "mecburen",
        "muhakkak",
        "muhtemelen",
        "mutlaka",
        "müstacelen",
        "müştereken",
        "müteakiben",
        "naçizane",
        "nadiren",
        "nakden",
        "naklen",
        "nazikane",
        "nerdeyse",
        "neredeyse",
        "nispeten",
        "nöbetleşe",
        "olabildiğince",
        "olduğunca",
        "ortaklaşa",
        "otomatikman",
        "öğlenleyin",
        "öğleyin",
        "öldüresiye",
        "ölesiye",
        "örfen",
        "öyle",
        "öylesine",
        "özellikle",
        "peşinen",
        "peşpeşe",
        "peyderpey",
        "ruhen",
        "sadece",
        "sahi",
        "sahiden",
        "salt",
        "salimen",
        "sanırım",
        "sanki",
        "sehven",
        "senlibenli",
        "sereserpe",
        "sırf",
        "sözgelimi",
        "sözgelişi",
        "şahsen",
        "şakacıktan",
        "şeklen",
        "şıppadak",
        "şimdilik",
        "şipşak",
        "tahminen",
        "takdiren",
        "takiben",
        "tamamen",
        "tamamiyle",
        "tedbiren",
        "temsilen",
        "tepetaklak",
        "tercihen",
        "tesadüfen",
        "tevekkeli",
        "tezelden",
        "tıbben",
        "tıkabasa",
        "tıpatıp",
        "toptan",
        "tümüyle",
        "uluorta",
        "usulcacık",
        "usulen",
        "üstünkörü",
        "vekaleten",
        "vicdanen",
        "yalancıktan",
        "yavaşçacık",
        "yekten",
        "yeniden",
        "yeterince",
        "yine",
        "yüzükoyun",
        "yüzüstü",
        "yüzyüze",
        "zaten",
        "zımmen",
        "zihnen",
        "zilzurna"
        ]

_postpositions = [
        "geçe",
        "gibi",
        "göre",
        "ilişkin",
        "kadar",
        "kala",
        "karşın",
        "nazaran"
        "rağmen",
        "üzere"
        ]

_subordinating_conjunctions = [
        "eğer",
        "madem",
        "mademki",
        "şayet"
        ]

_coordinating_conjunctions = [
        "ama",
        "hem",
        "fakat",
        "ila",
        "lakin",
        "ve",
        "veya",
        "veyahut"
        ]

MORPH_RULES = {
        "ADP": {word: {"POS": "ADP"} for word in _postpositions},
        "ADV": {word: {"POS": "ADV"} for word in _adverbs},
        "SCONJ": {word: {"POS": "SCONJ"} for word in _subordinating_conjunctions},
        "CCONJ": {word: {"POS": "CCONJ"} for word in _coordinating_conjunctions},
        "PRON": {
            "bana": {
                "LEMMA": "PRON_LEMMA",
                "POS": "PRON",
                "PronType": "Prs",
                "Person": "One",
                "Number": "Sing",
                "Case": "Dat"
                },
            "benden": {
                "LEMMA": "PRON_LEMMA",
                "POS": "PRON",
                "PronType": "Prs",
                "Person": "One",
                "Number": "Sing",
                "Case": "Abl"
                },
            "bende": {
                "LEMMA": "PRON_LEMMA",
                "POS": "PRON",
                "PronType": "Prs",
                "Person": "One",
                "Number": "Sing",
                "Case": "Loc"
                },
            "beni": {
                "LEMMA": "PRON_LEMMA",
                "POS": "PRON",
                "PronType": "Prs",
                "Person": "One",
                "Number": "Sing",
                "Case": "Acc"
                },
            "benle": {
                "LEMMA": "PRON_LEMMA",
                "POS": "PRON",
                "PronType": "Prs",
                "Person": "One",
                "Number": "Sing",
                "Case": "Ins"
                },
            "ben": {
                "LEMMA": "PRON_LEMMA",
                "POS": "PRON",
                "PronType": "Prs",
                "Person": "One",
                "Number": "Sing",
                "Case": "Nom"
                },
            "benim": {
                "LEMMA": "PRON_LEMMA",
                "POS": "PRON",
                "PronType": "Prs",
                "Person": "One",
                "Number": "Sing",
                "Case": "Gen"
                },
            "benimle": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Person": "One",
                    "Number": "Sing",
                    "Case": "Ins"
                    },
            "sana": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Person": "Two",
                    "Number": "Sing",
                    "Case": "Dat"
                    },
            "senden": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Person": "Two",
                    "Number": "Sing",
                    "Case": "Abl"
                    },
            "sende": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Person": "Two",
                    "Number": "Sing",
                    "Case": "Loc"
                    },
            "seni": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Person": "Two",
                    "Number": "Sing",
                    "Case": "Acc"
                    },
            "senle": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Person": "Two",
                    "Number": "Sing",
                    "Case": "Ins"
                    },
            "sen": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Person": "Two",
                    "Number": "Sing",
                    "Case": "Nom"
                    },
            "senin": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Person": "Two",
                    "Number": "Sing",
                    "Case": "Gen"
                    },
            "seninle": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Person": "Two",
                    "Number": "Sing",
                    "Case": "Ins"
                    },
            "ona": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "Person": "Three",
                    "Number": "Sing",
                    "Case": "Dat"
                    },
            "ondan": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "Person": "Three",
                    "Number": "Sing",
                    "Case": "Abl"
                    },
            "onda": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "Person": "",
                    "Number": "",
                    "Case": "Loc"
                    },
            "onu": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "Person": "Three",
                    "Number": "Sing",
                    "Case": "Acc"
                    },
            "onla": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "Person": "Three",
                    "Number": "Sing",
                    "Case": "Ins"
                    },
            "o": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "Person": "Three",
                    "Number": "Sing",
                    "Case": "Nom"
                    },
            "onun": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "Person": "Three",
                    "Number": "Sing",
                    "Case": "Gen"
                    },
            "onunla": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "Person": "Three",
                    "Number": "Sing",
                    "Case": "Ins"
                    },
            "bize": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Person": "One",
                    "Number": "Plur",
                    "Case": "Dat"
                    },
            "bizden": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Person": "One",
                    "Number": "Plur",
                    "Case": "Abl"
                    },
            "bizde": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Person": "One",
                    "Number": "Plur",
                    "Case": "Loc"
                    },
            "bizi": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Person": "One",
                    "Number": "Plur",
                    "Case": "Acc"
                    },
            "bizle": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Person": "One",
                    "Number": "Plur",
                    "Case": "Ins"
                    },
            "biz": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Person": "One",
                    "Number": "Plur",
                    "Case": "Nom"
                    },
            "bizim": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Person": "One",
                    "Number": "Plur",
                    "Case": "Gen"
                    },
            "bizimle": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Person": "One",
                    "Number": "Plur",
                    "Case": "Ins"
                    },
            "size": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Person": "Two",
                    "Number": "Plur",
                    "Case": "Dat"
                    },
            "sizden": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Person": "Two",
                    "Number": "Plur",
                    "Case": "Abl"
                    },
            "sizde": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Person": "Two",
                    "Number": "Plur",
                    "Case": "Loc"
                    },
            "sizi": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Person": "Two",
                    "Number": "Plur",
                    "Case": "Acc"
                    },
            "sizle": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Person": "Two",
                    "Number": "Plur",
                    "Case": "Ins"
                    },
            "siz": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Person": "Two",
                    "Number": "Plur",
                    "Case": "Nom"
                    },
            "sizin": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Person": "Two",
                    "Number": "Plur",
                    "Case": "Gen"
                    },
            "sizinle": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Person": "Two",
                    "Number": "Plur",
                    "Case": "Ins"
                    },
            "onlara": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "Person": "Three",
                    "Number": "Plur",
                    "Case": "Dat"
                    },
            "onlardan": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "Person": "Three",
                    "Number": "Plur",
                    "Case": "Abl"
                    },
            "onlarda": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "Person": "Three",
                    "Number": "Plur",
                    "Case": "Loc"
                    },
            "onları": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "Person": "Three",
                    "Number": "Plur",
                    "Case": "Acc"
                    },
            "onlarla": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "Person": "Three",
                    "Number": "Plur",
                    "Case": "Ins"
                    },
            "onlar": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "Person": "Three",
                    "Number": "Plur",
                    "Case": "Nom"
                    },
            "onların": {
                    "LEMMA": "PRON_LEMMA",
                    "POS": "PRON",
                    "Person": "Three",
                    "Number": "Plur",
                    "Case": "Gen"
                    },
            "buna": {
                    "LEMMA": "bu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Dat"
                    },
            "bundan": {
                    "LEMMA": "bu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Abl"
                    },
            "bunda": {
                    "LEMMA": "bu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Loc"
                    },
            "bunu": {
                    "LEMMA": "bu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Acc"
                    },
            "bunla": {
                    "LEMMA": "bu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Ins"
                    },
            "bu": {
                    "LEMMA": "bu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Nom"
                    },
            "bunun": {
                    "LEMMA": "bu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Gen"
                    },
            "bununla": {
                    "LEMMA": "bu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Ins"
                    },
            "şuna": {
                    "LEMMA": "şu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Dat"
                    },
            "şundan": {
                    "LEMMA": "şu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Abl"
                    },
            "şunda": {
                    "LEMMA": "şu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Loc"
                    },
            "şunu": {
                    "LEMMA": "şu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Acc"
                    },
            "şunla": {
                    "LEMMA": "şu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Ins"
                    },
            "şu": {
                    "LEMMA": "şu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Nom"
                    },
            "şunun": {
                    "LEMMA": "şu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Gen"
                    },
            "şununla": {
                    "LEMMA": "şu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Ins"
                    },
            "bunlara": {
                    "LEMMA": "bu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Dat"
                    },
            "bunlardan": {
                    "LEMMA": "bu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Abl"
                    },
            "bunlarda": {
                    "LEMMA": "bu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Loc"
                    },
            "bunları": {
                    "LEMMA": "bu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Acc"
                    },
            "bunlarla": {
                    "LEMMA": "bu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Ins"
                    },
            "bunlar": {
                    "LEMMA": "bu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Nom"
                    },
            "bunların": {
                    "LEMMA": "bu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Gen"
                    },
            "şunlara": {
                    "LEMMA": "şu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Dat"
                    },
            "şunlardan": {
                    "LEMMA": "şu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Abl"
                    },
            "şunlarda": {
                    "LEMMA": "şu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Loc"
                    },
            "şunları": {
                    "LEMMA": "şu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Acc"
                    },
            "şunlarla": {
                    "LEMMA": "şu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Ins"
                    },
            "şunlar": {
                    "LEMMA": "şu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Nom"
                    },
            "şunların": {
                    "LEMMA": "şu",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Gen"
                    },
            "buraya": {
                    "LEMMA": "bura",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Dat"
                    },
            "buradan": {
                    "LEMMA": "bura",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Abl"
                    },
            "burada": {
                    "LEMMA": "bura",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "loc.sg"
                    },
            "burayı": {
                    "LEMMA": "bura",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Acc"
                    },
            "burayla": {
                    "LEMMA": "bura",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Ins"
                    },
            "bura": {
                    "LEMMA": "bura",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Nom"
                    },
            "buranın": {
                    "LEMMA": "bura",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Gen"
                    },
            "şuraya": {
                    "LEMMA": "şura",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Dat"
                    },
            "şuradan": {
                    "LEMMA": "şura",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Abl"
                    },
            "şurada": {
                    "LEMMA": "şura",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "loc.sg"
                    },
            "şurayı": {
                    "LEMMA": "şura",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Acc"
                    },
            "şurayla": {
                    "LEMMA": "şura",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Ins"
                    },
            "şura": {
                    "LEMMA": "şura",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Nom"
                    },
            "şuranın": {
                    "LEMMA": "şura",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Gen"
                    },
            "oraya": {
                    "LEMMA": "ora",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Dat"
                    },
            "oradan": {
                    "LEMMA": "ora",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Abl"
                    },
            "orada": {
                    "LEMMA": "ora",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "loc.sg"
                    },
            "orayı": {
                    "LEMMA": "ora",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Acc"
                    },
            "orayla": {
                    "LEMMA": "ora",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Ins"
                    },
            "ora": {
                    "LEMMA": "ora",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Nom"
                    },
            "oranın": {
                    "LEMMA": "ora",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Sing",
                    "Case": "Gen"
                    },
            "buralarına": {
                    "LEMMA": "bura",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Dat"
                    },
            "buralarından": {
                    "LEMMA": "bura",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Abl"
                    },
            "buralarında": {
                    "LEMMA": "bura",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Loc"
                    },
            "buralarını": {
                    "LEMMA": "bura",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Acc"
                    },
            "buralarıyla": {
                    "LEMMA": "bura",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Ins"
                    },
            "buraları": {
                    "LEMMA": "bura",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Nom"
                    },
            "buralarının": {
                    "LEMMA": "bura",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Gen"
                    },
            "şuralarına": {
                    "LEMMA": "şura",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Dat"
                    },
            "şuralarından": {
                    "LEMMA": "şura",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Abl"
                    },
            "şuralarında": {
                    "LEMMA": "şura",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Loc"
                    },
            "şuralarını": {
                    "LEMMA": "şura",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Acc"
                    },
            "şuralarıyla": {
                    "LEMMA": "şura",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Ins"
                    },
            "şuraları": {
                    "LEMMA": "şura",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Nom"
                    },
            "şuralarının": {
                    "LEMMA": "şura",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Gen"
                    },
            "oralarına": {
                    "LEMMA": "ora",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Dat"
                    },
            "oralarından": {
                    "LEMMA": "ora",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Abl"
                    },
            "oralarında": {
                    "LEMMA": "ora",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Loc"
                    },
            "oralarını": {
                    "LEMMA": "ora",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Acc"
                    },
            "oralarıyla": {
                    "LEMMA": "ora",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Ins"
                    },
            "oraları": {
                    "LEMMA": "ora",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Nom"
                    },
            "oralarının": {
                    "LEMMA": "ora",
                    "POS": "PRON",
                    "PronType": "Dem",
                    "Number": "Plur",
                    "Case": "Gen"
                    }
            "kendime": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "One",
                    "Case": "dat",
                    "Number": "Sing"
                    },
            "kendimden": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "One",
                    "Case": "abl",
                    "Number": "Sing"
                    },
            "kendimde": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "One",
                    "Case": "loc",
                    "Number": "Sing"
                    },
            "kendimi": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "One",
                    "Case": "acc",
                    "Number": "Sing"
                    },
            "kendimle": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "One",
                    "Case": "instr",
                    "Number": "Sing"
                    },
            "kendim": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "One",
                    "Case": "nom",
                    "Number": "Sing"
                    },
            "kendimin": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "One",
                    "Case": "gen",
                    "Number": "Sing"
                    },
            "kendine": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Two",
                    "Case": "dat",
                    "Number": "Sing"
                    },
            "kendinden": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Two",
                    "Case": "abl",
                    "Number": "Sing"
                    },
            "kendinde": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Two",
                    "Case": "loc",
                    "Number": "Sing"
                    },
            "kendini": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Two",
                    "Case": "acc",
                    "Number": "Sing"
                    },
            "kendiyle": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Two",
                    "Case": "instr",
                    "Number": "Sing"
                    },
            "kendi": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Two",
                    "Case": "nom",
                    "Number": "Sing"
                    },
            "kendinin": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Two",
                    "Case": "gen",
                    "Number": "Sing"
                    },
            "kendisine": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Three",
                    "Case": "dat",
                    "Number": "Sing"
                    },
            "kendisinden": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Three",
                    "Case": "abl",
                    "Number": "Sing"
                    },
            "kendisinde": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Three",
                    "Case": "loc",
                    "Number": "Sing"
                    },
            "kendisini": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Three",
                    "Case": "acc",
                    "Number": "Sing"
                    },
            "kendisiyle": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Three",
                    "Case": "instr",
                    "Number": "Sing"
                    },
            "kendisi": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Three",
                    "Case": "nom",
                    "Number": "Sing"
                    },
            "kendisinin": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Three",
                    "Case": "gen",
                    "Number": "Sing"
                    },
            "kendimize": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "One",
                    "Case": "dat",
                    "Number": "Sing"
                    },
            "kendimizden": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "One",
                    "Case": "abl",
                    "Number": "Sing"
                    },
            "kendimizde": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "One",
                    "Case": "loc",
                    "Number": "Sing"
                    },
            "kendimizi": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "One",
                    "Case": "acc",
                    "Number": "Sing"
                    },
            "kendimizle": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "One",
                    "Case": "instr",
                    "Number": "Sing"
                    },
            "kendimiz": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "One",
                    "Case": "nom",
                    "Number": "Sing"
                    },
            "kendimizin": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "One",
                    "Case": "gen",
                    "Number": "Sing"
                    },
            "kendinize": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Two",
                    "Case": "dat",
                    "Number": "Sing"
                    },
            "kendinizden": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Two",
                    "Case": "abl",
                    "Number": "Sing"
                    },
            "kendinizde": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Two",
                    "Case": "loc",
                    "Number": "Sing"
                    },
            "kendinizi": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Two",
                    "Case": "acc",
                    "Number": "Sing"
                    },
            "kendinizle": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Two",
                    "Case": "instr",
                    "Number": "Sing"
                    },
            "kendiniz": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Two",
                    "Case": "nom",
                    "Number": "Sing"
                    },
            "kendinizin": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Two",
                    "Case": "gen",
                    "Number": "Sing"
                    },
            "kendilerine": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Three",
                    "Case": "dat",
                    "Number": "Sing"
                    },
            "kendilerinden": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Three",
                    "Case": "abl",
                    "Number": "Sing"
                    },
            "kendilerinde": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Three",
                    "Case": "loc",
                    "Number": "Sing"
                    },
            "kendilerini": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Three",
                    "Case": "acc",
                    "Number": "Sing"
                    },
            "kendileriyle": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Three",
                    "Case": "instr",
                    "Number": "Sing"
                    },
            "kendileriyken": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Three",
                    "Case": "nom",
                    "Number": "Sing"
                    },
            "kendilerinin": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Three",
                    "Case": "gen",
                    "Number": "Sing"
                    }
            }
    }


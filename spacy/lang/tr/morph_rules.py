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
                    },
            "kendime": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "One",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "kendimden": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "One",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "kendimde": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "One",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "kendimi": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "One",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "kendimle": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "One",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "kendim": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "One",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "kendimin": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "One",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "kendine": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Two",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "kendinden": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Two",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "kendinde": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Two",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "kendini": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Two",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "kendiyle": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Two",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "kendi": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Two",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "kendinin": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Two",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "kendisine": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Three",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "kendisinden": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Three",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "kendisinde": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Three",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "kendisini": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Three",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "kendisiyle": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Three",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "kendisi": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Three",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "kendisinin": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Three",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "kendimize": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "One",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "kendimizden": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "One",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "kendimizde": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "One",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "kendimizi": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "One",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "kendimizle": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "One",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "kendimiz": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "One",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "kendimizin": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "One",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "kendinize": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Two",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "kendinizden": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Two",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "kendinizde": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Two",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "kendinizi": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Two",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "kendinizle": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Two",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "kendiniz": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Two",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "kendinizin": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Two",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "kendilerine": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Three",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "kendilerinden": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Three",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "kendilerinde": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Three",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "kendilerini": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Three",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "kendileriyle": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Three",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "kendileriyken": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Three",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "kendilerinin": {
                    "LEMMA": "kendi",
                    "POS": "PRON",
                    "PronType": "Prs",
                    "Reflex": "Yes",
                    "Person": "Three",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "hangilerine": {
                    "LEMMA": "hangileri",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "hangilerinden": {
                    "LEMMA": "hangileri",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "hangilerinde": {
                    "LEMMA": "hangileri",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "hangilerini": {
                    "LEMMA": "hangileri",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "hangileriyle": {
                    "LEMMA": "hangileri",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "hangileri": {
                    "LEMMA": "hangileri",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "hangilerinin": {
                    "LEMMA": "hangileri",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "hangisine": {
                    "LEMMA": "hangi",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "hangisinden": {
                    "LEMMA": "hangi",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "hangisinde": {
                    "LEMMA": "hangi",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "hangisini": {
                    "LEMMA": "hangi",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "hangisiyle": {
                    "LEMMA": "hangi",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "hangisi": {
                    "LEMMA": "hangi",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "hangisinin": {
                    "LEMMA": "hangi",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "kime": {
                    "LEMMA": "kim",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "kimden": {
                    "LEMMA": "kim",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "kimde": {
                    "LEMMA": "kim",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "kimi": {
                    "LEMMA": "kim",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "kimle": {
                    "LEMMA": "kim",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "kim": {
                    "LEMMA": "kim",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "kimin": {
                    "LEMMA": "kim",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "kimlere": {
                    "LEMMA": "kim",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Dat",
                    "Number": "Plur"
                    },
            "kimlerden": {
                    "LEMMA": "kim",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Abl",
                    "Number": "Plur"
                    },
            "kimlerde": {
                    "LEMMA": "kim",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Loc",
                    "Number": "Plur"
                    },
            "kimleri": {
                    "LEMMA": "kim",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Acc",
                    "Number": "Plur"
                    },
            "kimlerle": {
                    "LEMMA": "kim",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Ins",
                    "Number": "Plur"
                    },
            "kimler": {
                    "LEMMA": "kim",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Nom",
                    "Number": "Plur"
                    },
            "kimlerin": {
                    "LEMMA": "kim",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Gen",
                    "Number": "Plur"
                    },
            "neye": {
                    "LEMMA": "ne",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "neden": {
                    "LEMMA": "ne",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "nede": {
                    "LEMMA": "ne",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "neyi": {
                    "LEMMA": "ne",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "neyle": {
                    "LEMMA": "ne",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "ne": {
                    "LEMMA": "ne",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "neyin": {
                    "LEMMA": "ne",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "nelere": {
                    "LEMMA": "ne",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Dat",
                    "Number": "Plur"
                    },
            "nelerden": {
                    "LEMMA": "ne",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Abl",
                    "Number": "Plur"
                    },
            "nelerde": {
                    "LEMMA": "ne",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Loc",
                    "Number": "Plur"
                    },
            "neleri": {
                    "LEMMA": "ne",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Acc",
                    "Number": "Plur"
                    },
            "nelerle": {
                    "LEMMA": "ne",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Ins",
                    "Number": "Plur"
                    },
            "neler": {
                    "LEMMA": "ne",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Nom",
                    "Number": "Plur"
                    },
            "nelerin": {
                    "LEMMA": "ne",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Gen",
                    "Number": "Plur"
                    },
            "nereye": {
                    "LEMMA": "nere",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "nereden": {
                    "LEMMA": "nere",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "nerede": {
                    "LEMMA": "nere",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "nereyi": {
                    "LEMMA": "nere",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "nereyle": {
                    "LEMMA": "nere",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "nere": {
                    "LEMMA": "nere",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "nerenin": {
                    "LEMMA": "nere",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "nerelere": {
                    "LEMMA": "nere",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Dat",
                    "Number": "Plur"
                    },
            "nerelerden": {
                    "LEMMA": "nere",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Abl",
                    "Number": "Plur"
                    },
            "nerelerde": {
                    "LEMMA": "nere",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Loc",
                    "Number": "Plur"
                    },
            "nereleri": {
                    "LEMMA": "nere",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Acc",
                    "Number": "Plur"
                    },
            "nerelerle": {
                    "LEMMA": "nere",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Ins",
                    "Number": "Plur"
                    },
            "nereler": {
                    "LEMMA": "nere",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Nom",
                    "Number": "Plur"
                    },
            "nerelerin": {
                    "LEMMA": "nere",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Gen",
                    "Number": "Plur"
                    },
            "kaçlarına": {
                    "LEMMA": "kaçları",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "kaçlarından": {
                    "LEMMA": "kaçları",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "kaçlarında": {
                    "LEMMA": "kaçları",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "kaçlarını": {
                    "LEMMA": "kaçları",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "kaçlarıyla": {
                    "LEMMA": "kaçları",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "kaçları": {
                    "LEMMA": "kaçı",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "kaçlarının": {
                    "LEMMA": "kaçları",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "kaçına": {
                    "LEMMA": "kaçı",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "kaçından": {
                    "LEMMA": "kaçı",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "kaçında": {
                    "LEMMA": "kaçı",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "kaçını": {
                    "LEMMA": "kaçı",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "kaçıyla": {
                    "LEMMA": "kaçı",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "kaçı": {
                    "LEMMA": "kaçı",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "kaçının": {
                    "LEMMA": "kaçı",
                    "POS": "PRON",
                    "PronType": "Int",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "başkasına": {
                    "LEMMA": "başkası",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "başkasından": {
                    "LEMMA": "başkası",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "başkasında": {
                    "LEMMA": "başkası",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "başkasını": {
                    "LEMMA": "başkası",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "başkasıyla": {
                    "LEMMA": "başkası",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "başkası": {
                    "LEMMA": "başkası",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "başkasının": {
                    "LEMMA": "başkası",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "başkalarına": {
                    "LEMMA": "başkaları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "başkalarından": {
                    "LEMMA": "başkaları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "başkalarında": {
                    "LEMMA": "başkaları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "başkalarını": {
                    "LEMMA": "başkaları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "başkalarıyla": {
                    "LEMMA": "başkaları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "başkaları": {
                    "LEMMA": "başkaları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "başkalarının": {
                    "LEMMA": "başkaları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "bazısına": {
                    "LEMMA": "bazısı",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "bazısından": {
                    "LEMMA": "bazısı",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "bazısında": {
                    "LEMMA": "bazısı",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "bazısını": {
                    "LEMMA": "bazısı",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "bazısıyla": {
                    "LEMMA": "bazısı",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "bazısı": {
                    "LEMMA": "bazısı",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "bazısının": {
                    "LEMMA": "bazısı",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "bazılarına": {
                    "LEMMA": "bazıları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "bazılarından": {
                    "LEMMA": "bazıları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "bazılarında": {
                    "LEMMA": "bazıları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "bazılarını": {
                    "LEMMA": "bazıları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "bazılarıyla": {
                    "LEMMA": "bazıları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "bazıları": {
                    "LEMMA": "bazıları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "bazılarının": {
                    "LEMMA": "bazıları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "birbirine": {
                    "LEMMA": "birbir",
                    "POS": "PRON",
                    "PronType": "Rcp",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "birbirinden": {
                    "LEMMA": "birbir",
                    "POS": "PRON",
                    "PronType": "Rcp",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "birbirinde": {
                    "LEMMA": "birbir",
                    "POS": "PRON",
                    "PronType": "Rcp",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "birbirini": {
                    "LEMMA": "birbir",
                    "POS": "PRON",
                    "PronType": "Rcp",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "birbiriyle": {
                    "LEMMA": "birbir",
                    "POS": "PRON",
                    "PronType": "Rcp",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "birbiri": {
                    "LEMMA": "birbiri",
                    "POS": "PRON",
                    "PronType": "Rcp",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "birbirinin": {
                    "LEMMA": "birbir",
                    "POS": "PRON",
                    "PronType": "Rcp",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "birbirlerine": {
                    "LEMMA": "birbir",
                    "POS": "PRON",
                    "PronType": "Rcp",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "birbirlerinden": {
                    "LEMMA": "birbir",
                    "POS": "PRON",
                    "PronType": "Rcp",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "birbirlerinde": {
                    "LEMMA": "birbir",
                    "POS": "PRON",
                    "PronType": "Rcp",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "birbirlerini": {
                    "LEMMA": "birbir",
                    "POS": "PRON",
                    "PronType": "Rcp",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "birbirleriyle": {
                    "LEMMA": "birbir",
                    "POS": "PRON",
                    "PronType": "Rcp",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "birbirleri": {
                    "LEMMA": "birbir",
                    "POS": "PRON",
                    "PronType": "Rcp",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "birbirlerinin": {
                    "LEMMA": "birbir",
                    "POS": "PRON",
                    "PronType": "Rcp",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "birçoğuna": {
                    "LEMMA": "birçoğu",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "birçoğundan": {
                    "LEMMA": "birçoğu",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "birçoğunda": {
                    "LEMMA": "birçoğu",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "birçoğunu": {
                    "LEMMA": "birçoğu",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "birçoğuyla": {
                    "LEMMA": "birçoğu",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "birçoğu": {
                    "LEMMA": "birçoğu",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "birçoğunun": {
                    "LEMMA": "birçoğu",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "birçoklarına": {
                    "LEMMA": "birçokları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "birçoklarından": {
                    "LEMMA": "birçokları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "birçoklarında": {
                    "LEMMA": "birçokları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "birçoklarını": {
                    "LEMMA": "birçokları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "birçoklarıyla": {
                    "LEMMA": "birçokları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "birçokları": {
                    "LEMMA": "birçokları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "birçoklarının": {
                    "LEMMA": "birçokları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "birilerine": {
                    "LEMMA": "birileri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "birilerinden": {
                    "LEMMA": "birileri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "birilerinde": {
                    "LEMMA": "birileri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "birilerini": {
                    "LEMMA": "birileri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "birileriyle": {
                    "LEMMA": "birileri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "birileri": {
                    "LEMMA": "birileri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "birilerinin": {
                    "LEMMA": "birileri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "birisine": {
                    "LEMMA": "biri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "birisinden": {
                    "LEMMA": "biri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "birisinde": {
                    "LEMMA": "biri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "birisini": {
                    "LEMMA": "biri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "birisiyle": {
                    "LEMMA": "biri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "birisi": {
                    "LEMMA": "biri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "birisinin": {
                    "LEMMA": "biri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "birkaçına": {
                    "LEMMA": "birkaçı",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "birkaçından": {
                    "LEMMA": "birkaçı",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "birkaçında": {
                    "LEMMA": "birkaçı",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "birkaçını": {
                    "LEMMA": "birkaçı",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "birkaçıyla": {
                    "LEMMA": "birkaçı",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "birkaçı": {
                    "LEMMA": "birkaç",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "birkaçının": {
                    "LEMMA": "birkaçı",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "birtakımına": {
                    "LEMMA": "birtakımı",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "birtakımından": {
                    "LEMMA": "birtakımı",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "birtakımında": {
                    "LEMMA": "birtakımı",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "birtakımını": {
                    "LEMMA": "birtakımı",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "birtakımıyla": {
                    "LEMMA": "birtakımı",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "birtakımı": {
                    "LEMMA": "birtakımı",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "birtakımının": {
                    "LEMMA": "birtakımı",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "böylesine": {
                    "LEMMA": "böylesi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "böylesinden": {
                    "LEMMA": "böylesi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "böylesinde": {
                    "LEMMA": "böylesi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "böylesini": {
                    "LEMMA": "böylesi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "böylesiyle": {
                    "LEMMA": "böylesi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "böylesi": {
                    "LEMMA": "böylesi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "böylesinin": {
                    "LEMMA": "böylesi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "şöylesine": {
                    "LEMMA": "şöylesi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "şöylesinden": {
                    "LEMMA": "şöylesi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "şöylesinde": {
                    "LEMMA": "şöylesi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "şöylesini": {
                    "LEMMA": "şöylesi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "şöylesiyle": {
                    "LEMMA": "şöylesi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "şöylesi": {
                    "LEMMA": "şöylesi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "şöylesinin": {
                    "LEMMA": "şöylesi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "öylesine": {
                    "LEMMA": "öylesi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "öylesinden": {
                    "LEMMA": "öylesi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "öylesinde": {
                    "LEMMA": "öylesi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "öylesini": {
                    "LEMMA": "öylesi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "öylesiyle": {
                    "LEMMA": "öylesi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "öylesi": {
                    "LEMMA": "öylesi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "öylesinin": {
                    "LEMMA": "öylesi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "böylelerine": {
                    "LEMMA": "böyleleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "böylelerinden": {
                    "LEMMA": "böyleleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "böylelerinde": {
                    "LEMMA": "böyleleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "böylelerini": {
                    "LEMMA": "böyleleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "böyleleriyle": {
                    "LEMMA": "böyleleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "böyleleri": {
                    "LEMMA": "böyleleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "böylelerinin": {
                    "LEMMA": "böyleleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "şöylelerine": {
                    "LEMMA": "şöyleleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "şöylelerinden": {
                    "LEMMA": "şöyleleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "şöylelerinde": {
                    "LEMMA": "şöyleleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "şöylelerini": {
                    "LEMMA": "şöyleleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "şöyleleriyle": {
                    "LEMMA": "şöyleleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "şöyleleri": {
                    "LEMMA": "şöyleleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "şöylelerinin": {
                    "LEMMA": "şöyleleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "öylelerine": {
                    "LEMMA": "öyleleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "öylelerinden": {
                    "LEMMA": "öyleleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "öylelerinde": {
                    "LEMMA": "öyleleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "öylelerini": {
                    "LEMMA": "öyleleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "öyleleriyle": {
                    "LEMMA": "öyleleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "öyleleri": {
                    "LEMMA": "öyleleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "öylelerinin": {
                    "LEMMA": "öyleleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "çoklarına": {
                    "LEMMA": "çokları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "çoklarından": {
                    "LEMMA": "çokları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "çoklarında": {
                    "LEMMA": "çokları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "çoklarını": {
                    "LEMMA": "çokları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "çoklarıyla": {
                    "LEMMA": "çokları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "çokları": {
                    "LEMMA": "çokları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "çoklarının": {
                    "LEMMA": "çokları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "çoğuna": {
                    "LEMMA": "çoğu",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "çoğundan": {
                    "LEMMA": "çoğu",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "çoğunda": {
                    "LEMMA": "çoğu",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "çoğunu": {
                    "LEMMA": "çoğu",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "çoğuyla": {
                    "LEMMA": "çoğu",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "çoğu": {
                    "LEMMA": "çoğu",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "çoğunun": {
                    "LEMMA": "çoğu",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "diğerine": {
                    "LEMMA": "diğeri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "diğerinden": {
                    "LEMMA": "diğeri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "diğerinde": {
                    "LEMMA": "diğeri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "diğerini": {
                    "LEMMA": "diğeri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "diğeriyle": {
                    "LEMMA": "diğeri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "diğeri": {
                    "LEMMA": "diğer",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "diğerinin": {
                    "LEMMA": "diğeri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "diğerlerine": {
                    "LEMMA": "diğerleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "diğerlerinden": {
                    "LEMMA": "diğerleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "diğerlerinde": {
                    "LEMMA": "diğerleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "diğerlerini": {
                    "LEMMA": "diğerleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "diğerleriyle": {
                    "LEMMA": "diğerleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "diğerleri": {
                    "LEMMA": "diğerleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "diğerlerinin": {
                    "LEMMA": "diğerleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "hepinize": {
                    "LEMMA": "hepiniz",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "hepinizden": {
                    "LEMMA": "hepiniz",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "hepinizde": {
                    "LEMMA": "hepiniz",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "hepinizi": {
                    "LEMMA": "hepiniz",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "hepinizle": {
                    "LEMMA": "hepiniz",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "hepiniz": {
                    "LEMMA": "hepiniz",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "hepinizin": {
                    "LEMMA": "hepiniz",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "hepimize": {
                    "LEMMA": "hepimiz",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "hepimizden": {
                    "LEMMA": "hepimiz",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "hepimizde": {
                    "LEMMA": "hepimiz",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "hepimizi": {
                    "LEMMA": "hepimiz",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "hepimizle": {
                    "LEMMA": "hepimiz",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "hepimiz": {
                    "LEMMA": "hepimiz",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "hepimizin": {
                    "LEMMA": "hepimiz",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "hepsine": {
                    "LEMMA": "hepsi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "hepsinden": {
                    "LEMMA": "hepsi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "hepsinde": {
                    "LEMMA": "hepsi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "hepsini": {
                    "LEMMA": "hepsi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "hepsiyle": {
                    "LEMMA": "hepsi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "hepsi": {
                    "LEMMA": "hepsi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "hepsinin": {
                    "LEMMA": "hepsi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "herbirine": {
                    "LEMMA": "herbiri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "herbirinden": {
                    "LEMMA": "herbiri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "herbirinde": {
                    "LEMMA": "herbiri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "herbirini": {
                    "LEMMA": "herbiri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "herbiriyle": {
                    "LEMMA": "herbiri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "herbiri": {
                    "LEMMA": "herbiri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "herbirinin": {
                    "LEMMA": "herbiri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "herbirlerine": {
                    "LEMMA": "herbirleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "herbirlerinden": {
                    "LEMMA": "herbirleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "herbirlerinde": {
                    "LEMMA": "herbirleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "herbirlerini": {
                    "LEMMA": "herbirleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "herbirleriyle": {
                    "LEMMA": "herbirleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "herbirleri": {
                    "LEMMA": "herbirleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "herbirlerinin": {
                    "LEMMA": "herbirleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "herhangisine": {
                    "LEMMA": "herhangisi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "herhangisinden": {
                    "LEMMA": "herhangisi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "herhangisinde": {
                    "LEMMA": "herhangisi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "herhangisini": {
                    "LEMMA": "herhangisi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "herhangisiyle": {
                    "LEMMA": "herhangisi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "herhangisi": {
                    "LEMMA": "herhangisi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "herhangisinin": {
                    "LEMMA": "herhangisi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "herhangilerine": {
                    "LEMMA": "herhangileri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "herhangilerinden": {
                    "LEMMA": "herhangileri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "herhangilerinde": {
                    "LEMMA": "herhangileri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "herhangilerini": {
                    "LEMMA": "herhangileri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "herhangileriyle": {
                    "LEMMA": "herhangileri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "herhangileri": {
                    "LEMMA": "herhangileri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "herhangilerinin": {
                    "LEMMA": "herhangileri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "herkese": {
                    "LEMMA": "herkes",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "herkesten": {
                    "LEMMA": "herkes",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "herkeste": {
                    "LEMMA": "herkes",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "herkesi": {
                    "LEMMA": "herkes",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "herkesle": {
                    "LEMMA": "herkes",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "herkes": {
                    "LEMMA": "herkes",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "herkesin": {
                    "LEMMA": "herkes",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "hiçbirisine": {
                    "LEMMA": "hiçbiri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "hiçbirisinden": {
                    "LEMMA": "hiçbiri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "hiçbirisinde": {
                    "LEMMA": "hiçbiri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "hiçbirisini": {
                    "LEMMA": "hiçbiri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "hiçbirisiyle": {
                    "LEMMA": "hiçbiri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "hiçbirisi": {
                    "LEMMA": "hiçbiri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "hiçbirisinin": {
                    "LEMMA": "hiçbiri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "hiçbirine": {
                    "LEMMA": "hiçbiri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "hiçbirinden": {
                    "LEMMA": "hiçbiri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "hiçbirinde": {
                    "LEMMA": "hiçbiri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "hiçbirini": {
                    "LEMMA": "hiçbiri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "hiçbiriyle": {
                    "LEMMA": "hiçbiri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "hiçbiri": {
                    "LEMMA": "hiçbiri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "hiçbirinin": {
                    "LEMMA": "hiçbiri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "kimisine": {
                    "LEMMA": "kimi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "kimisinden": {
                    "LEMMA": "kimi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "kimisinde": {
                    "LEMMA": "kimi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "kimisini": {
                    "LEMMA": "kimi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "kimisiyle": {
                    "LEMMA": "kimi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "kimisi": {
                    "LEMMA": "kimi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "kimisinin": {
                    "LEMMA": "kimi",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "kimilerine": {
                    "LEMMA": "kimileri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "kimilerinden": {
                    "LEMMA": "kimileri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "kimilerinde": {
                    "LEMMA": "kimileri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "kimilerini": {
                    "LEMMA": "kimileri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "kimileriyle": {
                    "LEMMA": "kimileri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "kimileri": {
                    "LEMMA": "kimileri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "kimilerinin": {
                    "LEMMA": "kimileri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "kimseye": {
                    "LEMMA": "kimse",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "kimseden": {
                    "LEMMA": "kimse",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "kimsede": {
                    "LEMMA": "kimse",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "kimseyi": {
                    "LEMMA": "kimse",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "kimseyle": {
                    "LEMMA": "kimse",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "kimse": {
                    "LEMMA": "kimse",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "kimsenin": {
                    "LEMMA": "kimse",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "öbürüne": {
                    "LEMMA": "öbürü",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "öbüründen": {
                    "LEMMA": "öbürü",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "öbüründe": {
                    "LEMMA": "öbürü",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "öbürünü": {
                    "LEMMA": "öbürü",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "öbürüyle": {
                    "LEMMA": "öbürü",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "öbürü": {
                    "LEMMA": "öbürü",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "öbürünün": {
                    "LEMMA": "öbürü",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "öbürlerine": {
                    "LEMMA": "öbürleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "öbürlerinden": {
                    "LEMMA": "öbürleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "öbürlerinde": {
                    "LEMMA": "öbürleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "öbürlerini": {
                    "LEMMA": "öbürleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "öbürleriyle": {
                    "LEMMA": "öbürleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "öbürleri": {
                    "LEMMA": "öbürleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "öbürlerinin": {
                    "LEMMA": "öbürleri",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "ötekisine": {
                    "LEMMA": "öteki",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "ötekisinden": {
                    "LEMMA": "öteki",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "ötekisinde": {
                    "LEMMA": "öteki",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "ötekisini": {
                    "LEMMA": "öteki",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "ötekisiyle": {
                    "LEMMA": "öteki",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "ötekisi": {
                    "LEMMA": "öteki",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "ötekisinin": {
                    "LEMMA": "öteki",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "pekçoğuna": {
                    "LEMMA": "pekçoğu",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "pekçoğundan": {
                    "LEMMA": "pekçoğu",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "pekçoğunda": {
                    "LEMMA": "pekçoğu",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "pekçoğunu": {
                    "LEMMA": "pekçoğu",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "pekçoğuyla": {
                    "LEMMA": "pekçoğu",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "pekçoğu": {
                    "LEMMA": "pekçoğu",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "pekçoğunun": {
                    "LEMMA": "pekçoğu",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    },
            "pekçoklarına": {
                    "LEMMA": "pekçokları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Dat",
                    "Number": "Sing"
                    },
            "pekçoklarından": {
                    "LEMMA": "pekçokları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Abl",
                    "Number": "Sing"
                    },
            "pekçoklarında": {
                    "LEMMA": "pekçokları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Loc",
                    "Number": "Sing"
                    },
            "pekçoklarını": {
                    "LEMMA": "pekçokları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Acc",
                    "Number": "Sing"
                    },
            "pekçoklarıyla": {
                    "LEMMA": "pekçokları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Ins",
                    "Number": "Sing"
                    },
            "pekçokları": {
                    "LEMMA": "pekçokları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Nom",
                    "Number": "Sing"
                    },
            "pekçoklarının": {
                    "LEMMA": "pekçokları",
                    "POS": "PRON",
                    "PronType": "Ind",
                    "Case": "Gen",
                    "Number": "Sing"
                    }
            }
    }

for tag, rules in MORPH_RULES.items():
    for key, attrs in dict(rules).items():
        rules[key.title()] = attrs

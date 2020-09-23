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
		    }

	    }
    }


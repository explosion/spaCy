# coding: utf8
from __future__ import unicode_literals

from ...symbols import LEMMA, PRON_LEMMA

_subordinating_conjunctions = [
    "кога",
    "штом",
    "штотуку",
    "тукушто",
    "откако",
    "откога",
    "пред да ",
    "дури",
    "додека",
    "затоа што",
    "зашто",
    "бидејќи",
    "поради тоа што",
    "дека",
    "оти",
    "така што",
    "да",
    "за да",
    "ако",
    "без да",
    "ли",
    "иако",
    "макар што",
    "и покрај тоа што",
    "и да",
    "така како што",
    "како да",
    "како божем",
    "што",
    "кој",
    "којшто",
    "чиј",
    "чијшто",
    "дали",
    "каков што",
    "колкав што",
    "каде што",
    "како што",
    "колку што",
    "како",
]

_part = [
    "де",
    "бе",
    "ма",
    "барем",
    "пак",
    "меѓутоа",
    "просто",
    "да",
    "не",
    "ниту",
    "зар",
    "ли",
    "дали",
    "единствено",
    "само",
    "точно",
    "токму",
    "скоро",
    "речиси",
    "рамно",
    "нека",
    "ќе",
    "уште",
    "притоа",
    "исто така",
    "би",
]
_modal_verbs = [
    "може",
    "мора",
    "треба",
]

sum_aux = [
    "сум",
    "си",
    "е",
    "сме",
    "сте",
    "се",
]

MORPH_RULES = {
    "SUM": {word: {"POS": "AUX"} for word in sum_aux},
    "IMA": {
        "има": {"POS": "VERB"},
        "имала": {"POS": "VERB"},
        "имало": {"POS": "VERB"},
        "имал": {"POS": "VERB"},
        "имале": {"POS": "VERB"},
        "имав": {"POS": "VERB"},
        "имавте": {"POS": "VERB"},
        "имаа": {"POS": "VERB"},
        "имаше": {"POS": "VERB"},
        "имам": {"POS": "AUX"},
        "имаш": {"POS": "AUX"},
        "имаме": {"POS": "AUX"},
        "имате": {"POS": "AUX"},
        "имаат": {"POS": "AUX"},
        "имавме": {"POS": "AUX"},
    },
    "MD": {word: {"POS": "VERB"} for word in _modal_verbs},
    "NN": {
        "нешто": {"POS": "PRON"},
        "некој": {"POS": "PRON"},
        "некоја": {"POS": "PRON"},
        "некое": {"POS": "PRON"},
        "некои": {"POS": "PRON"},
        "ништо": {"POS": "PRON"},
    },
    "PRP": {
        "јас": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "One",
            "Number": "Sing",
            "Case": "Nom",
        },
        "мене": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "One",
            "Number": "Sing",
            "Case": "Acc",
        },
        "ме": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "One",
            "Number": "Sing",
            "Case": "Acc",
        },
        "ми": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "One",
            "Number": "Sing",
            "Case": "Dat",
        },
        "ти": {LEMMA: PRON_LEMMA, "POS": "PRON", "PronType": "Prs", "Person": "Two", "Number": "Sing", "Case": "Nom"},
        "тебе": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "Two",
            "Number": "Sing",
            "Case": "Acc",
        },
        "те": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "Two",
            "Number": "Sing",
            "Case": "Acc",
        },
        "тој": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "Three",
            "Number": "Sing",
            "Gender": "Masc",
            "Case": "Nom",
        },
        "него": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "Three",
            "Number": "Sing",
            "Gender": "Masc",
            "Case": "Acc",
        },
        "го": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "Three",
            "Number": "Sing",
            "Gender": "Masc",
            "Case": "Acc",
        },
        "нему": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "Three",
            "Number": "Sing",
            "Gender": "Masc",
            "Case": "Dat",
        },
        "му": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "Three",
            "Number": "Sing",
            "Gender": "Masc",
            "Case": "Dat",
        },
        "таа": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "Three",
            "Number": "Sing",
            "Gender": "Fem",
            "Case": "Nom",
        },
        "неа": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "Three",
            "Number": "Sing",
            "Gender": "Fem",
            "Case": "Acc",
        },
        "ја": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "Three",
            "Number": "Sing",
            "Gender": "Fem",
            "Case": "Acc",
        },
        "нејзе": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "Three",
            "Number": "Sing",
            "Gender": "Fem",
            "Case": "Dat",
        },
        "ѝ": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "Three",
            "Number": "Sing",
            "Gender": "Fem",
            "Case": "Dat",
        },
        "тоа": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "Three",
            "Number": "Sing",
            "Gender": "Neut",
        },
        "ние": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "One",
            "Number": "Plur",
            "Case": "Nom",
        },
        "нас": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "One",
            "Number": "Plur",
            "Case": "Acc",
        },
        "нѐ": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "One",
            "Number": "Plur",
            "Case": "Acc",
        },
        "нам": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "One",
            "Number": "Plur",
            "Case": "Dat",
        },
        "ни": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "One",
            "Number": "Plur",
            "Case": "Dat",
        },
        "вие": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "Two",
            "Number": "Plur",
            "Case": "Nom",
        },
        "вас": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "Two",
            "Number": "Plur",
            "Case": "Acc",
        },
        "ве": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "Two",
            "Number": "Plur",
            "Case": "Acc",
        },
        "вам": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "Two",
            "Number": "Plur",
            "Case": "Dat",
        },
        "ви": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "Two",
            "Number": "Plur",
            "Case": "Dat",
        },
        "тие": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "Three",
            "Number": "Plur",
            "Case": "Nom",
        },
        "нив": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "Three",
            "Number": "Plur",
            "Case": "Acc",
        },
        "ги": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "Three",
            "Number": "Plur",
            "Case": "Acc",
        },
        "ним": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "Three",
            "Number": "Plur",
            "Case": "Dat",
        },
        "им": {
            LEMMA: PRON_LEMMA,
            "POS": "PRON",
            "PronType": "Prs",
            "Person": "Three",
            "Number": "Plur",
            "Case": "Dat",
        },

    },

    "VB": {
        word: {"POS": "AUX"}
        for word in ["сум", "има"]
    },
    "VBT": {
        "бев ": {
            LEMMA: "сум",
            "POS": "AUX",
            "VerbForm": "Fin",
            "Tense": "Past",
            "Person": "one"
        },

        "имав": {
            LEMMA: "има",
            "POS": "AUX",
            "VerbForm": "Fin",
            "Tense": "Past",
            "Person": "one"

        },

    },
    "VBM": {
        "беше ": {
            LEMMA: "сум",
            "POS": "AUX",
            "VerbForm": "Fin",
            "Tense": "Past",
            "Person": "two"
        },
        "имаше": {
            LEMMA: "има",
            "POS": "AUX",
            "VerbForm": "Fin",
            "Tense": "Past",
            "Person": "two"

        },

    },
    "VBK": {
        "било ": {
            LEMMA: "сум",
            "POS": "AUX",
            "VerbForm": "Fin",
            "Tense": "Past",
            "Gender": "Neut",
            "Person": "three",
        },
        "била ": {
            LEMMA: "сум",
            "POS": "AUX",
            "VerbForm": "Fin",
            "Tense": "Past",
            "Gender": "Fem",
            "Person": "three",

        },
        "бил ": {
            LEMMA: "сум",
            "POS": "AUX",
            "VerbForm": "Fin",
            "Tense": "Past",
            "Gender": "Masc",
            "Person": "three",

        },
        "беше ": {
            LEMMA: "сум",
            "POS": "AUX",
            "VerbForm": "Fin",
            "Tense": "Past",
            "Person": "three",
            "Person": "three",
        },
        "имаше": {
            LEMMA: "има",
            "POS": "AUX",
            "VerbForm": "Fin",
            "Tense": "Past",
            "Person": "three",
        },

    },
    "VBTT": {
        "бевме ": {
            LEMMA: "сум",
            "POS": "AUX",
            "VerbForm": "Fin",
            "Tense": "Past",

        },
        "имавме": {
            LEMMA: "има",
            "POS": "AUX",
            "VerbForm": "Fin",
            "Tense": "Past",

        },

    },
    "VBMM": {
        "бевте ": {
            LEMMA: "сум",
            "POS": "AUX",
            "VerbForm": "Fin",
            "Tense": "Past",

        },
        "имавте": {
            LEMMA: "има",
            "POS": "AUX",
            "VerbForm": "Fin",
            "Tense": "Past",

        },

    },
    "VBKK": {
        "биле ": {
            LEMMA: "сум",
            "POS": "AUX",
            "VerbForm": "Fin",
            "Tense": "Past",
            "Gender": "Plur",

        },
        "беа ": {
            LEMMA: "сум",
            "POS": "AUX",
            "VerbForm": "Fin",
            "Tense": "Past",

        },
        "имаа": {
            LEMMA: "има",
            "POS": "AUX",
            "VerbForm": "Fin",
            "Tense": "Past",

        },

    },
    "VBP": {
        "сум ": {
            LEMMA: "сум",
            "POS": "AUX",
            "VerbForm": "Fin",
            "Tense": "Pres",

        },
        "имам": {
            LEMMA: "има",
            "POS": "AUX",
            "VerbForm": "Fin",
            "Tense": "Pres",

        },

    },
    "VBV": {
        "си ": {
            LEMMA: "сум",
            "POS": "AUX",
            "VerbForm": "Fin",
            "Tense": "Pres",

        },
        "имаш": {
            LEMMA: "има",
            "POS": "AUX",
            "VerbForm": "Fin",
            "Tense": "Pres",

        },

    },
    "VBZ": {
        "е ": {
            LEMMA: "сум",
            "POS": "AUX",
            "VerbForm": "Fin",
            "Tense": "Pres",

        },
        "има": {
            LEMMA: "има",
            "POS": "AUX",
            "VerbForm": "Fin",
            "Tense": "Pres",

        },

    },
    "VBPP": {
        "сме": {
            LEMMA: "сум",
            "POS": "AUX",
            "VerbForm": "Fin",
            "Tense": "Pres",
            "Number": "Plur",
        },
        "имаме": {
            LEMMA: "има",
            "POS": "AUX",
            "VerbForm": "Fin",
            "Tense": "Pres",
            "Number": "Plur",
        },
    },
    "VBVV": {
        "сте": {
            LEMMA: "сум",
            "POS": "AUX",
            "VerbForm": "Fin",
            "Tense": "Pres",
            "Number": "Plur",
        },
        "имате": {
            LEMMA: "има",
            "POS": "AUX",
            "VerbForm": "Fin",
            "Tense": "Pres",
            "Number": "Plur",
        },

    },
    "VBZZ": {
        "се": {
            LEMMA: "сум",
            "POS": "AUX",
            "VerbForm": "Fin",
            "Tense": "Pres",
            "Number": "Plur",
        },
        "имаат": {
            LEMMA: "има",
            "POS": "AUX",
            "VerbForm": "Fin",
            "Tense": "Past",
            "Number": "Plur",
        },

    },

}

for tag, rules in MORPH_RULES.items():
    for key, attrs in dict(rules).items():
        rules[key.title()] = attrs

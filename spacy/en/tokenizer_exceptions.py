# encoding: utf8
from __future__ import unicode_literals

from ..symbols import *
from ..language_data import PRON_LEMMA


EXC = {}

EXCLUDE_EXC = ["Ill", "ill", "Its", "its", "Hell", "hell", "Shell", "shell", "Shed", "shed", "were", "Were", "Well", "well", "Whore", "whore"]


# Pronouns

for pron in ["i"]:
    for orth in [pron, pron.title()]:
        EXC[orth + "'m"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "'m", LEMMA: "be", TAG: "VBP", "tenspect": 1, "number": 1}
        ]

        EXC[orth + "m"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "m", LEMMA: "be", TAG: "VBP", "tenspect": 1, "number": 1 }
        ]

        EXC[orth + "'ma"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "'m", LEMMA: "be", NORM: "am"},
            {ORTH: "a", LEMMA: "going to", NORM: "gonna"}
        ]

        EXC[orth + "ma"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "m", LEMMA: "be", NORM: "am"},
            {ORTH: "a", LEMMA: "going to", NORM: "gonna"}
        ]


for pron in ["i", "you", "he", "she", "it", "we", "they"]:
    for orth in [pron, pron.title()]:
        EXC[orth + "'ll"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "'ll", LEMMA: "will", TAG: "MD"}
        ]

        EXC[orth + "ll"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "ll", LEMMA: "will", TAG: "MD"}
        ]

        EXC[orth + "'ll've"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "'ll", LEMMA: "will", TAG: "MD"},
            {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
        ]

        EXC[orth + "llve"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "ll", LEMMA: "will", TAG: "MD"},
            {ORTH: "ve", LEMMA: "have", TAG: "VB"}
        ]

        EXC[orth + "'d"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "'d", LEMMA: "would", TAG: "MD"}
        ]

        EXC[orth + "d"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "d", LEMMA: "would", TAG: "MD"}
        ]

        EXC[orth + "'d've"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "'d", LEMMA: "would", TAG: "MD"},
            {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
        ]

        EXC[orth + "dve"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "d", LEMMA: "would", TAG: "MD"},
            {ORTH: "ve", LEMMA: "have", TAG: "VB"}
        ]


for pron in ["i", "you", "we", "they"]:
    for orth in [pron, pron.title()]:
        EXC[orth + "'ve"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
        ]

        EXC[orth + "ve"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "ve", LEMMA: "have", TAG: "VB"}
        ]


for pron in ["you", "we", "they"]:
    for orth in [pron, pron.title()]:
        EXC[orth + "'re"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "'re", LEMMA: "be", NORM: "are"}
        ]

        EXC[orth + "re"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "re", LEMMA: "be", NORM: "are"}
        ]


for pron in ["he", "she", "it"]:
    for orth in [pron, pron.title()]:
        EXC[orth + "'s"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "'s"}
        ]

        EXC[orth + "s"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "s"}
        ]



# W-words, relative pronouns, prepositions etc.

for word in ["who", "what", "when", "where", "why", "how", "there", "that"]:
    for orth in [word, word.title()]:
        EXC[orth + "'s"] = [
            {ORTH: orth, LEMMA: word},
            {ORTH: "'s"}
        ]

        EXC[orth + "s"] = [
            {ORTH: orth, LEMMA: word},
            {ORTH: "s"}
        ]

        EXC[orth + "'ll"] = [
            {ORTH: orth, LEMMA: word},
            {ORTH: "'ll", LEMMA: "will", TAG: "MD"}
        ]

        EXC[orth + "ll"] = [
            {ORTH: orth, LEMMA: word},
            {ORTH: "ll", LEMMA: "will", TAG: "MD"}
        ]

        EXC[orth + "'ll've"] = [
            {ORTH: orth, LEMMA: word},
            {ORTH: "'ll", LEMMA: "will", TAG: "MD"},
            {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
        ]

        EXC[orth + "llve"] = [
            {ORTH: orth, LEMMA: word},
            {ORTH: "ll", LEMMA: "will", TAG: "MD"},
            {ORTH: "ve", LEMMA: "have", TAG: "VB"}
        ]

        EXC[orth + "'re"] = [
            {ORTH: orth, LEMMA: word},
            {ORTH: "'re", LEMMA: "be", NORM: "are"}
        ]

        EXC[orth + "re"] = [
            {ORTH: orth, LEMMA: word},
            {ORTH: "re", LEMMA: "be", NORM: "are"}
        ]

        EXC[orth + "'ve"] = [
            {ORTH: orth},
            {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
        ]

        EXC[orth + "ve"] = [
            {ORTH: orth, LEMMA: word},
            {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
        ]

        EXC[orth + "'d"] = [
            {ORTH: orth, LEMMA: word},
            {ORTH: "'d"}
        ]

        EXC[orth + "d"] = [
            {ORTH: orth, LEMMA: word},
            {ORTH: "d"}
        ]

        EXC[orth + "'d've"] = [
            {ORTH: orth, LEMMA: word},
            {ORTH: "'d", LEMMA: "would", TAG: "MD"},
            {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
        ]

        EXC[orth + "dve"] = [
            {ORTH: orth, LEMMA: word},
            {ORTH: "d", LEMMA: "would", TAG: "MD"},
            {ORTH: "ve", LEMMA: "have", TAG: "VB"}
        ]


# Verbs

for verb_data in [
    {ORTH: "ca", LEMMA: "can", TAG: "MD"},
    {ORTH: "could", TAG: "MD"},
    {ORTH: "do", LEMMA: "do"},
    {ORTH: "does", LEMMA: "do"},
    {ORTH: "did", LEMMA: "do", TAG: "VBD"},
    {ORTH: "had", LEMMA: "have", TAG: "VBD"},
    {ORTH: "may"},
    {ORTH: "might"},
    {ORTH: "must"},
    {ORTH: "need"},
    {ORTH: "ought"},
    {ORTH: "sha", LEMMA: "shall"},
    {ORTH: "should"},
    {ORTH: "wo", LEMMA: "will"},
    {ORTH: "would"}
]:
    verb_data_tc = dict(verb_data)
    verb_data_tc[ORTH] = verb_data_tc[ORTH].title()

    for data in [verb_data, verb_data_tc]:
        EXC[data[ORTH] + "n't"] = [
            dict(data),
            {ORTH: "n't", LEMMA: "not", TAG: "RB"}
        ]

        EXC[data[ORTH] + "nt"] = [
            dict(data),
            {ORTH: "nt", LEMMA: "not", TAG: "RB"}
        ]

        EXC[data[ORTH] + "n't've"] = [
            dict(data),
            {ORTH: "n't", LEMMA: "not", TAG: "RB"},
            {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
        ]

        EXC[data[ORTH] + "ntve"] = [
            dict(data),
            {ORTH: "nt", LEMMA: "not", TAG: "RB"},
            {ORTH: "ve", LEMMA: "have", TAG: "VB"}
        ]


for verb_data in [
    {ORTH: "could", TAG: "MD"},
    {ORTH: "might"},
    {ORTH: "must"},
    {ORTH: "should"}
]:
    verb_data_tc = dict(verb_data)
    verb_data_tc[ORTH] = verb_data_tc[ORTH].title()

    for data in [verb_data, verb_data_tc]:
        EXC[data[ORTH] + "'ve"] = [
            dict(data),
            {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
        ]

        EXC[data[ORTH] + "ve"] = [
            dict(data),
            {ORTH: "ve", LEMMA: "have", TAG: "VB"}
        ]


for verb_data in [
    {ORTH: "ai", TAG: "VBP", "number": 2, LEMMA: "be"},
    {ORTH: "are", LEMMA: "be", TAG: "VBP", "number": 2},
    {ORTH: "is", LEMMA: "be", TAG: "VBZ"},
    {ORTH: "was", LEMMA: "be"},
    {ORTH: "were", LEMMA: "be"}
]:
    verb_data_tc = dict(verb_data)
    verb_data_tc[ORTH] = verb_data_tc[ORTH].title()

    for data in [verb_data, verb_data_tc]:
        EXC[data[ORTH] + "n't"] = [
            dict(data),
            {ORTH: "n't", LEMMA: "not", TAG: "RB"}
        ]

        EXC[data[ORTH] + "nt"] = [
            dict(data),
            {ORTH: "nt", LEMMA: "not", TAG: "RB"}
        ]



# Other contractions with trailing apostrophe

for exc_data in [
    {ORTH: "doin", LEMMA: "do", NORM: "doing"},
    {ORTH: "goin", LEMMA: "go", NORM: "going"},
    {ORTH: "nothin", LEMMA: "nothing"},
    {ORTH: "nuthin", LEMMA: "nothing"},
    {ORTH: "ol", LEMMA: "old"},
    {ORTH: "somethin", LEMMA: "something"}
]:
    exc_data_tc = dict(exc_data)
    exc_data_tc[ORTH] = exc_data_tc[ORTH].title()

    for data in [exc_data, exc_data_tc]:
        data_apos = dict(data)
        data_apos[ORTH] = data_apos[ORTH] + "'"

        EXC[data[ORTH]] = [
            dict(data)
        ]

        EXC[data_apos[ORTH]] = [
            dict(data_apos)
        ]


# Other contractions with leading apostrophe

for exc_data in [
    {ORTH: "cause", LEMMA: "because"},
    {ORTH: "em", LEMMA: PRON_LEMMA, NORM: "them"},
    {ORTH: "ll", LEMMA: "will"},
    {ORTH: "nuff", LEMMA: "enough"}
]:
    exc_data_apos = dict(exc_data)
    exc_data_apos[ORTH] = "'" + exc_data_apos[ORTH]

    for data in [exc_data, exc_data_apos]:
        EXC[data[ORTH]] = [
            dict(data)
        ]


# Rest

OTHER = {
    " ": [
        {ORTH: " ", TAG: "SP"}
    ],

    "\u00a0": [
        {ORTH: "\u00a0", TAG: "SP", LEMMA: "  "}
    ],

    "'S": [
        {ORTH: "'S", LEMMA: "'s"}
    ],

    "'s": [
        {ORTH: "'s", LEMMA: "'s"}
    ],

    "'re": [
        {ORTH: "'re", LEMMA: "be", NORM: "are"}
    ],

    "\u2018S": [
        {ORTH: "\u2018S", LEMMA: "'s"}
    ],

    "\u2018s": [
        {ORTH: "\u2018s", LEMMA: "'s"}
    ],

    "and/or": [
        {ORTH: "and/or", LEMMA: "and/or", TAG: "CC"}
    ],

    "'Cause": [
        {ORTH: "'Cause", LEMMA: "because"}
    ],

    "y'all": [
        {ORTH: "y'", LEMMA: PRON_LEMMA, NORM: "you"},
        {ORTH: "all"}
    ],

    "yall": [
        {ORTH: "y", LEMMA: PRON_LEMMA, NORM: "you"},
        {ORTH: "all"}
    ],

    "ma'am": [
        {ORTH: "ma'am", LEMMA: "madam"}
    ],

    "Ma'am": [
        {ORTH: "Ma'am", LEMMA: "madam"}
    ],

    "o'clock": [
        {ORTH: "o'clock", LEMMA: "o'clock"}
    ],

    "O'clock": [
        {ORTH: "O'clock", LEMMA: "o'clock"}
    ],

    "how'd'y": [
        {ORTH: "how", LEMMA: "how"},
        {ORTH: "'d", LEMMA: "do"},
        {ORTH: "'y", LEMMA: PRON_LEMMA, NORM: "you"}
    ],

    "How'd'y": [
        {ORTH: "How", LEMMA: "how"},
        {ORTH: "'d", LEMMA: "do"},
        {ORTH: "'y", LEMMA: PRON_LEMMA, NORM: "you"}
    ],

    "not've": [
        {ORTH: "not", LEMMA: "not", TAG: "RB"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "notve": [
        {ORTH: "not", LEMMA: "not", TAG: "RB"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "Not've": [
        {ORTH: "Not", LEMMA: "not", TAG: "RB"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}
    ],

    "Notve": [
        {ORTH: "Not", LEMMA: "not", TAG: "RB"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}
    ],

    "cannot": [
        {ORTH: "can", LEMMA: "can", TAG: "MD"},
        {ORTH: "not", LEMMA: "not", TAG: "RB"}
    ],

    "Cannot": [
        {ORTH: "Can", LEMMA: "can", TAG: "MD"},
        {ORTH: "not", LEMMA: "not", TAG: "RB"}
    ],

    "gonna": [
        {ORTH: "gon", LEMMA: "go", NORM: "going"},
        {ORTH: "na", LEMMA: "to"}
    ],

    "Gonna": [
        {ORTH: "Gon", LEMMA: "go", NORM: "going"},
        {ORTH: "na", LEMMA: "to"}
    ],

    "gotta": [
        {ORTH: "got"},
        {ORTH: "ta", LEMMA: "to"}
    ],

    "Gotta": [
        {ORTH: "Got"},
        {ORTH: "ta", LEMMA: "to"}
    ],

    "let's": [
        {ORTH: "let"},
        {ORTH: "'s", LEMMA: PRON_LEMMA, NORM: "us"}
    ],

    "Let's": [
        {ORTH: "Let", LEMMA: "let"},
        {ORTH: "'s", LEMMA: PRON_LEMMA, NORM: "us"}
    ],

    "\u2014": [
        {ORTH: "\u2014", TAG: ":", LEMMA: "--"}
    ],

    "\n": [
        {ORTH: "\n", TAG: "SP"}
    ],

    "\t": [
        {ORTH: "\t", TAG: "SP"}
    ]
}


# Abbreviations

ABBREVIATIONS = {
    "Mt.": [
        {ORTH: "Mt.", LEMMA: "Mount"}
    ],

    "Ak.": [
        {ORTH: "Ak.", LEMMA: "Alaska"}
    ],

    "Ala.": [
        {ORTH: "Ala.", LEMMA: "Alabama"}
    ],

    "Apr.": [
        {ORTH: "Apr.", LEMMA: "April"}
    ],

    "Ariz.": [
        {ORTH: "Ariz.", LEMMA: "Arizona"}
    ],

    "Ark.": [
        {ORTH: "Ark.", LEMMA: "Arkansas"}
    ],

    "Aug.": [
        {ORTH: "Aug.", LEMMA: "August"}
    ],

    "Calif.": [
        {ORTH: "Calif.", LEMMA: "California"}
    ],

    "Colo.": [
        {ORTH: "Colo.", LEMMA: "Colorado"}
    ],

    "Conn.": [
        {ORTH: "Conn.", LEMMA: "Connecticut"}
    ],

    "Dec.": [
        {ORTH: "Dec.", LEMMA: "December"}
    ],

    "Del.": [
        {ORTH: "Del.", LEMMA: "Delaware"}
    ],

    "Feb.": [
        {ORTH: "Feb.", LEMMA: "February"}
    ],

    "Fla.": [
        {ORTH: "Fla.", LEMMA: "Florida"}
    ],

    "Ga.": [
        {ORTH: "Ga.", LEMMA: "Georgia"}
    ],

    "Ia.": [
        {ORTH: "Ia.", LEMMA: "Iowa"}
    ],

    "Id.": [
        {ORTH: "Id.", LEMMA: "Idaho"}
    ],

    "Ill.": [
        {ORTH: "Ill.", LEMMA: "Illinois"}
    ],

    "Ind.": [
        {ORTH: "Ind.", LEMMA: "Indiana"}
    ],

    "Jan.": [
        {ORTH: "Jan.", LEMMA: "January"}
    ],

    "Jul.": [
        {ORTH: "Jul.", LEMMA: "July"}
    ],

    "Jun.": [
        {ORTH: "Jun.", LEMMA: "June"}
    ],

    "Kan.": [
        {ORTH: "Kan.", LEMMA: "Kansas"}
    ],

    "Kans.": [
        {ORTH: "Kans.", LEMMA: "Kansas"}
    ],

    "Ky.": [
        {ORTH: "Ky.", LEMMA: "Kentucky"}
    ],

    "La.": [
        {ORTH: "La.", LEMMA: "Louisiana"}
    ],

    "Mar.": [
        {ORTH: "Mar.", LEMMA: "March"}
    ],

    "Mass.": [
        {ORTH: "Mass.", LEMMA: "Massachusetts"}
    ],

    "May.": [
        {ORTH: "May.", LEMMA: "May"}
    ],

    "Mich.": [
        {ORTH: "Mich.", LEMMA: "Michigan"}
    ],

    "Minn.": [
        {ORTH: "Minn.", LEMMA: "Minnesota"}
    ],

    "Miss.": [
        {ORTH: "Miss.", LEMMA: "Mississippi"}
    ],

    "N.C.": [
        {ORTH: "N.C.", LEMMA: "North Carolina"}
    ],

    "N.D.": [
        {ORTH: "N.D.", LEMMA: "North Dakota"}
    ],

    "N.H.": [
        {ORTH: "N.H.", LEMMA: "New Hampshire"}
    ],

    "N.J.": [
        {ORTH: "N.J.", LEMMA: "New Jersey"}
    ],

    "N.M.": [
        {ORTH: "N.M.", LEMMA: "New Mexico"}
    ],

    "N.Y.": [
        {ORTH: "N.Y.", LEMMA: "New York"}
    ],

    "Neb.": [
        {ORTH: "Neb.", LEMMA: "Nebraska"}
    ],

    "Nebr.": [
        {ORTH: "Nebr.", LEMMA: "Nebraska"}
    ],

    "Nev.": [
        {ORTH: "Nev.", LEMMA: "Nevada"}
    ],

    "Nov.": [
        {ORTH: "Nov.", LEMMA: "November"}
    ],

    "Oct.": [
        {ORTH: "Oct.", LEMMA: "October"}
    ],

    "Okla.": [
        {ORTH: "Okla.", LEMMA: "Oklahoma"}
    ],

    "Ore.": [
        {ORTH: "Ore.", LEMMA: "Oregon"}
    ],

    "Pa.": [
        {ORTH: "Pa.", LEMMA: "Pennsylvania"}
    ],

    "S.C.": [
        {ORTH: "S.C.", LEMMA: "South Carolina"}
    ],

    "Sep.": [
        {ORTH: "Sep.", LEMMA: "September"}
    ],

    "Sept.": [
        {ORTH: "Sept.", LEMMA: "September"}
    ],

    "Tenn.": [
        {ORTH: "Tenn.", LEMMA: "Tennessee"}
    ],

    "Va.": [
        {ORTH: "Va.", LEMMA: "Virginia"}
    ],

    "Wash.": [
        {ORTH: "Wash.", LEMMA: "Washington"}
    ],

    "Wis.": [
        {ORTH: "Wis.", LEMMA: "Wisconsin"}
    ]
}


TOKENIZER_EXCEPTIONS = dict(EXC)
TOKENIZER_EXCEPTIONS.update(OTHER)
TOKENIZER_EXCEPTIONS.update(ABBREVIATIONS)


# Remove EXCLUDE_EXC if in exceptions

for string in EXCLUDE_EXC:
    if string in TOKENIZER_EXCEPTIONS:
        TOKENIZER_EXCEPTIONS.pop(string)


# Abbreviations with only one ORTH token

ORTH_ONLY = [
    "'d",
    "a.m.",
    "Adm.",
    "Bros.",
    "co.",
    "Co.",
    "Corp.",
    "D.C.",
    "Dr.",
    "e.g.",
    "E.g.",
    "E.G.",
    "Gen.",
    "Gov.",
    "i.e.",
    "I.e.",
    "I.E.",
    "Inc.",
    "Jr.",
    "Ltd.",
    "Md.",
    "Messrs.",
    "Mo.",
    "Mont.",
    "Mr.",
    "Mrs.",
    "Ms.",
    "p.m.",
    "Ph.D.",
    "Rep.",
    "Rev.",
    "Sen.",
    "St.",
    "vs."
]

# encoding: utf8
from __future__ import unicode_literals

from ...symbols import LEMMA, PRON_LEMMA

# This dict includes all the PRON and DET tag combinations found in the
# dataset developed by Schibsted, Nasjonalbiblioteket and LTG (to be published
# autumn 2018) and the rarely used polite form.

MORPH_RULES = {
    "PRON__Animacy=Anim|Case=Nom|Number=Sing|Person=1|PronType=Prs": {
        "jeg": {
            LEMMA: PRON_LEMMA,
            "PronType": "Prs",
            "Person": "One",
            "Number": "Sing",
            "Case": "Nom",
        }
    },
    "PRON__Animacy=Anim|Case=Nom|Number=Sing|Person=2|PronType=Prs": {
        "du": {
            LEMMA: PRON_LEMMA,
            "PronType": "Prs",
            "Person": "Two",
            "Number": "Sing",
            "Case": "Nom",
        },
        # polite form, not sure about the tag
        "De": {
            LEMMA: PRON_LEMMA,
            "PronType": "Prs",
            "Person": "Two",
            "Number": "Sing",
            "Case": "Nom",
            "Polite": "Form",
        },
    },
    "PRON__Animacy=Anim|Case=Nom|Gender=Fem|Number=Sing|Person=3|PronType=Prs": {
        "hun": {
            LEMMA: PRON_LEMMA,
            "PronType": "Prs",
            "Person": "Three",
            "Number": "Sing",
            "Gender": "Fem",
            "Case": "Nom",
        }
    },
    "PRON__Animacy=Anim|Case=Nom|Gender=Masc|Number=Sing|Person=3|PronType=Prs": {
        "han": {
            LEMMA: PRON_LEMMA,
            "PronType": "Prs",
            "Person": "Three",
            "Number": "Sing",
            "Gender": "Masc",
            "Case": "Nom",
        }
    },
    "PRON__Gender=Neut|Number=Sing|Person=3|PronType=Prs": {
        "det": {
            LEMMA: PRON_LEMMA,
            "PronType": "Prs",
            "Person": "Three",
            "Number": "Sing",
            "Gender": "Neut",
        },
        "alt": {
            LEMMA: PRON_LEMMA,
            "PronType": "Prs",
            "Person": "Three",
            "Number": "Sing",
            "Gender": "Neut",
        },
        "intet": {
            LEMMA: PRON_LEMMA,
            "PronType": "Prs",
            "Person": "Three",
            "Number": "Sing",
            "Gender": "Neut",
        },
        "noe": {
            LEMMA: PRON_LEMMA,
            "PronType": "Prs",
            "Number": "Sing",
            "Person": "Three",
            "Gender": "Neut",
        },
    },
    "PRON__Animacy=Anim|Case=Nom|Number=Plur|Person=1|PronType=Prs": {
        "vi": {
            LEMMA: PRON_LEMMA,
            "PronType": "Prs",
            "Person": "One",
            "Number": "Plur",
            "Case": "Nom",
        }
    },
    "PRON__Animacy=Anim|Case=Nom|Number=Plur|Person=2|PronType=Prs": {
        "dere": {
            LEMMA: PRON_LEMMA,
            "PronType": "Prs",
            "Person": "Two",
            "Number": "Plur",
            "Case": "Nom",
        }
    },
    "PRON__Case=Nom|Number=Plur|Person=3|PronType=Prs": {
        "de": {
            LEMMA: PRON_LEMMA,
            "PronType": "Prs",
            "Person": "Three",
            "Number": "Plur",
            "Case": "Nom",
        }
    },
    "PRON__Animacy=Anim|Case=Acc|Number=Sing|Person=1|PronType=Prs": {
        "meg": {
            LEMMA: PRON_LEMMA,
            "PronType": "Prs",
            "Person": "One",
            "Number": "Sing",
            "Case": "Acc",
        }
    },
    "PRON__Animacy=Anim|Case=Acc|Number=Sing|Person=2|PronType=Prs": {
        "deg": {
            LEMMA: PRON_LEMMA,
            "PronType": "Prs",
            "Person": "Two",
            "Number": "Sing",
            "Case": "Acc",
        },
        # polite form, not sure about the tag
        "Dem": {
            LEMMA: PRON_LEMMA,
            "PronType": "Prs",
            "Person": "Two",
            "Number": "Sing",
            "Case": "Acc",
            "Polite": "Form",
        },
    },
    "PRON__Animacy=Anim|Case=Acc|Gender=Fem|Number=Sing|Person=3|PronType=Prs": {
        "henne": {
            LEMMA: PRON_LEMMA,
            "PronType": "Prs",
            "Person": "Three",
            "Number": "Sing",
            "Gender": "Fem",
            "Case": "Acc",
        }
    },
    "PRON__Animacy=Anim|Case=Acc|Gender=Masc|Number=Sing|Person=3|PronType=Prs": {
        "ham": {
            LEMMA: PRON_LEMMA,
            "PronType": "Prs",
            "Person": "Three",
            "Number": "Sing",
            "Gender": "Masc",
            "Case": "Acc",
        },
        "han": {
            LEMMA: PRON_LEMMA,
            "PronType": "Prs",
            "Person": "Three",
            "Number": "Sing",
            "Gender": "Masc",
            "Case": "Acc",
        },
    },
    "PRON__Animacy=Anim|Case=Acc|Number=Plur|Person=1|PronType=Prs": {
        "oss": {
            LEMMA: PRON_LEMMA,
            "PronType": "Prs",
            "Person": "One",
            "Number": "Plur",
            "Case": "Acc",
        }
    },
    "PRON__Animacy=Anim|Case=Acc|Number=Plur|Person=2|PronType=Prs": {
        "dere": {
            LEMMA: PRON_LEMMA,
            "PronType": "Prs",
            "Person": "Two",
            "Number": "Plur",
            "Case": "Acc",
        }
    },
    "PRON__Case=Acc|Number=Plur|Person=3|PronType=Prs": {
        "dem": {
            LEMMA: PRON_LEMMA,
            "PronType": "Prs",
            "Person": "Three",
            "Number": "Plur",
            "Case": "Acc",
        }
    },
    "PRON__Case=Acc|Reflex=Yes": {
        "seg": {
            LEMMA: PRON_LEMMA,
            "Person": "Three",
            "Number": ("Sing", "Plur"),
            "Reflex": "Yes",
        }
    },
    "PRON__Animacy=Anim|Case=Nom|Number=Sing|PronType=Prs": {
        "man": {LEMMA: PRON_LEMMA, "PronType": "Prs", "Number": "Sing", "Case": "Nom"}
    },
    "DET__Gender=Masc|Number=Sing|Poss=Yes": {
        "min": {
            LEMMA: "min",
            "Person": "One",
            "Number": "Sing",
            "Poss": "Yes",
            "Gender": "Masc",
        },
        "din": {
            LEMMA: "din",
            "Person": "Two",
            "Number": "Sing",
            "Poss": "Yes",
            "Gender": "Masc",
        },
        "hennes": {
            LEMMA: "hennes",
            "Person": "Three",
            "Number": "Sing",
            "Poss": "Yes",
            "Gender": "Masc",
        },
        "hans": {
            LEMMA: "hans",
            "Person": "Three",
            "Number": "Sing",
            "Poss": "Yes",
            "Gender": "Masc",
        },
        "sin": {
            LEMMA: "sin",
            "Person": "Three",
            "Number": "Sing",
            "Poss": "Yes",
            "Gender": "Masc",
            "Reflex": "Yes",
        },
        "vår": {
            LEMMA: "vår",
            "Person": "One",
            "Number": "Sing",
            "Poss": "Yes",
            "Gender": "Masc",
        },
        "deres": {
            LEMMA: "deres",
            "Person": ("Two", "Three"),
            "Number": "Sing",
            "Poss": "Yes",
            "Gender": "Masc",
        },
        # polite form, not sure about the tag
        "Deres": {
            LEMMA: "Deres",
            "Person": "Three",
            "Number": "Sing",
            "Poss": "Yes",
            "Gender": "Masc",
            "Polite": "Form",
        },
    },
    "DET__Gender=Fem|Number=Sing|Poss=Yes": {
        "mi": {
            LEMMA: "min",
            "Person": "One",
            "Number": "Sing",
            "Poss": "Yes",
            "Gender": "Fem",
        },
        "di": {
            LEMMA: "din",
            "Person": "Two",
            "Number": "Sing",
            "Poss": "Yes",
            "Gender": "Fem",
        },
        "hennes": {
            LEMMA: "hennes",
            "Person": "Three",
            "Number": "Sing",
            "Poss": "Yes",
            "Gender": "Fem",
        },
        "hans": {
            LEMMA: "hans",
            "Person": "Three",
            "Number": "Sing",
            "Poss": "Yes",
            "Gender": "Fem",
        },
        "si": {
            LEMMA: "sin",
            "Person": "Three",
            "Number": "Sing",
            "Poss": "Yes",
            "Gender": "Fem",
            "Reflex": "Yes",
        },
        "vår": {
            LEMMA: "vår",
            "Person": "One",
            "Number": "Sing",
            "Poss": "Yes",
            "Gender": "Fem",
        },
        "deres": {
            LEMMA: "deres",
            "Person": ("Two", "Three"),
            "Number": "Sing",
            "Poss": "Yes",
            "Gender": "Fem",
        },
        # polite form, not sure about the tag
        "Deres": {
            LEMMA: "Deres",
            "Person": "Three",
            "Number": "Sing",
            "Poss": "Yes",
            "Gender": "Fem",
            "Polite": "Form",
        },
    },
    "DET__Gender=Neut|Number=Sing|Poss=Yes": {
        "mitt": {
            LEMMA: "min",
            "Person": "One",
            "Number": "Sing",
            "Poss": "Yes",
            "Gender": "Neut",
        },
        "ditt": {
            LEMMA: "din",
            "Person": "Two",
            "Number": "Sing",
            "Poss": "Yes",
            "Gender": "Neut",
        },
        "hennes": {
            LEMMA: "hennes",
            "Person": "Three",
            "Number": "Sing",
            "Poss": "Yes",
            "Gender": "Neut",
        },
        "hans": {
            LEMMA: "hans",
            "Person": "Three",
            "Number": "Sing",
            "Poss": "Yes",
            "Gender": "Neut",
        },
        "sitt": {
            LEMMA: "sin",
            "Person": "Three",
            "Number": "Sing",
            "Poss": "Yes",
            "Gender": "Neut",
            "Reflex": "Yes",
        },
        "vårt": {
            LEMMA: "vår",
            "Person": "One",
            "Number": "Sing",
            "Poss": "Yes",
            "Gender": "Neut",
        },
        "deres": {
            LEMMA: "deres",
            "Person": ("Two", "Three"),
            "Number": "Sing",
            "Poss": "Yes",
            "Gender": "Neut",
        },
        # polite form, not sure about the tag
        "Deres": {
            LEMMA: "Deres",
            "Person": "Three",
            "Number": "Sing",
            "Poss": "Yes",
            "Gender": "Neut",
            "Polite": "Form",
        },
    },
    "DET__Number=Plur|Poss=Yes": {
        "mine": {LEMMA: "min", "Person": "One", "Number": "Plur", "Poss": "Yes"},
        "dine": {LEMMA: "din", "Person": "Two", "Number": "Plur", "Poss": "Yes"},
        "hennes": {LEMMA: "hennes", "Person": "Three", "Number": "Plur", "Poss": "Yes"},
        "hans": {LEMMA: "hans", "Person": "Three", "Number": "Plur", "Poss": "Yes"},
        "sine": {
            LEMMA: "sin",
            "Person": "Three",
            "Number": "Plur",
            "Poss": "Yes",
            "Reflex": "Yes",
        },
        "våre": {LEMMA: "vår", "Person": "One", "Number": "Plur", "Poss": "Yes"},
        "deres": {
            LEMMA: "deres",
            "Person": ("Two", "Three"),
            "Number": "Plur",
            "Poss": "Yes",
        },
    },
    "PRON__Animacy=Anim|Number=Plur|PronType=Rcp": {
        "hverandre": {LEMMA: PRON_LEMMA, "PronType": "Rcp", "Number": "Plur"}
    },
    "DET__Number=Plur|Poss=Yes|PronType=Rcp": {
        "hverandres": {
            LEMMA: "hverandres",
            "PronType": "Rcp",
            "Number": "Plur",
            "Poss": "Yes",
        }
    },
    "PRON___": {"som": {LEMMA: PRON_LEMMA}, "ikkenoe": {LEMMA: PRON_LEMMA}},
    "PRON__PronType=Int": {"hva": {LEMMA: PRON_LEMMA, "PronType": "Int"}},
    "PRON__Animacy=Anim|PronType=Int": {"hvem": {LEMMA: PRON_LEMMA, "PronType": "Int"}},
    "PRON__Animacy=Anim|Poss=Yes|PronType=Int": {
        "hvis": {LEMMA: PRON_LEMMA, "PronType": "Int", "Poss": "Yes"}
    },
    "PRON__Number=Plur|Person=3|PronType=Prs": {
        "noen": {
            LEMMA: PRON_LEMMA,
            "PronType": "Prs",
            "Number": "Plur",
            "Person": "Three",
        },
        "ingen": {
            LEMMA: PRON_LEMMA,
            "PronType": "Prs",
            "Number": "Plur",
            "Person": "Three",
        },
        "alle": {
            LEMMA: PRON_LEMMA,
            "PronType": "Prs",
            "Number": "Plur",
            "Person": "Three",
        },
    },
    "PRON__Gender=Fem,Masc|Number=Sing|Person=3|PronType=Prs": {
        "noen": {
            LEMMA: PRON_LEMMA,
            "PronType": "Prs",
            "Number": "Sing",
            "Person": "Three",
            "Gender": ("Fem", "Masc"),
        },
        "den": {
            LEMMA: PRON_LEMMA,
            "PronType": "Prs",
            "Number": "Sing",
            "Person": "Three",
            "Gender": ("Fem", "Masc"),
        },
        "ingen": {
            LEMMA: PRON_LEMMA,
            "PronType": "Prs",
            "Number": "Sing",
            "Person": "Three",
            "Gender": ("Fem", "Masc"),
            "Polarity": "Neg",
        },
    },
    "PRON__Number=Sing": {"ingenting": {LEMMA: PRON_LEMMA, "Number": "Sing"}},
    "PRON__Animacy=Anim|Number=Sing|PronType=Prs": {
        "en": {LEMMA: PRON_LEMMA, "PronType": "Prs", "Number": "Sing"}
    },
    "PRON__Animacy=Anim|Case=Gen,Nom|Number=Sing|PronType=Prs": {
        "ens": {
            LEMMA: PRON_LEMMA,
            "PronType": "Prs",
            "Number": "Sing",
            "Case": ("Gen", "Nom"),
        }
    },
    "PRON__Animacy=Anim|Case=Gen|Number=Sing|PronType=Prs": {
        "ens": {LEMMA: PRON_LEMMA, "PronType": "Prs", "Number": "Sing", "Case": "Gen"}
    },
    "DET__Case=Gen|Gender=Masc|Number=Sing": {
        "ens": {LEMMA: "en", "Number": "Sing", "Case": "Gen"}
    },
    "DET__Gender=Masc|Number=Sing": {
        "enhver": {LEMMA: "enhver", "Number": "Sing", "Gender": "Masc"},
        "all": {LEMMA: "all", "Number": "Sing", "Gender": "Masc"},
        "hver": {LEMMA: "hver", "Number": "Sing", "Gender": "Masc"},
        "noen": {LEMMA: "noen", "Gender": "Masc", "Number": "Sing"},
        "noe": {LEMMA: "noen", "Gender": "Masc", "Number": "Sing"},
        "en": {LEMMA: "en", "Number": "Sing", "Gender": "Neut"},
        "ingen": {LEMMA: "ingen", "Gender": "Masc", "Number": "Sing"},
    },
    "DET__Gender=Fem|Number=Sing": {
        "enhver": {LEMMA: "enhver", "Number": "Sing", "Gender": "Fem"},
        "all": {LEMMA: "all", "Number": "Sing", "Gender": "Fem"},
        "hver": {LEMMA: "hver", "Number": "Sing", "Gender": "Fem"},
        "noen": {LEMMA: "noen", "Gender": "Fem", "Number": "Sing"},
        "noe": {LEMMA: "noen", "Gender": "Fem", "Number": "Sing"},
        "ei": {LEMMA: "en", "Number": "Sing", "Gender": "Fem"},
    },
    "DET__Gender=Neut|Number=Sing": {
        "ethvert": {LEMMA: "enhver", "Number": "Sing", "Gender": "Neut"},
        "alt": {LEMMA: "all", "Number": "Sing", "Gender": "Neut"},
        "hvert": {LEMMA: "hver", "Number": "Sing", "Gender": "Neut"},
        "noe": {LEMMA: "noen", "Number": "Sing", "Gender": "Neut"},
        "intet": {LEMMA: "ingen", "Gender": "Neut", "Number": "Sing"},
        "et": {LEMMA: "en", "Number": "Sing", "Gender": "Neut"},
    },
    "DET__Gender=Neut|Number=Sing|PronType=Int": {
        "hvilket": {
            LEMMA: "hvilken",
            "PronType": "Int",
            "Number": "Sing",
            "Gender": "Neut",
        }
    },
    "DET__Gender=Fem|Number=Sing|PronType=Int": {
        "hvilken": {
            LEMMA: "hvilken",
            "PronType": "Int",
            "Number": "Sing",
            "Gender": "Fem",
        }
    },
    "DET__Gender=Masc|Number=Sing|PronType=Int": {
        "hvilken": {
            LEMMA: "hvilken",
            "PronType": "Int",
            "Number": "Sing",
            "Gender": "Masc",
        }
    },
    "DET__Number=Plur|PronType=Int": {
        "hvilke": {LEMMA: "hvilken", "PronType": "Int", "Number": "Plur"}
    },
    "DET__Number=Plur": {
        "alle": {LEMMA: "all", "Number": "Plur"},
        "noen": {LEMMA: "noen", "Number": "Plur"},
        "egne": {LEMMA: "egen", "Number": "Plur"},
        "ingen": {LEMMA: "ingen", "Number": "Plur"},
    },
    "DET__Gender=Masc|Number=Sing|PronType=Dem": {
        "den": {LEMMA: "den", "PronType": "Dem", "Number": "Sing", "Gender": "Masc"},
        "slik": {LEMMA: "slik", "PronType": "Dem", "Number": "Sing", "Gender": "Masc"},
        "denne": {
            LEMMA: "denne",
            "PronType": "Dem",
            "Number": "Sing",
            "Gender": "Masc",
        },
    },
    "DET__Gender=Fem|Number=Sing|PronType=Dem": {
        "den": {LEMMA: "den", "PronType": "Dem", "Number": "Sing", "Gender": "Fem"},
        "slik": {LEMMA: "slik", "PronType": "Dem", "Number": "Sing", "Gender": "Fem"},
        "denne": {LEMMA: "denne", "PronType": "Dem", "Number": "Sing", "Gender": "Fem"},
    },
    "DET__Gender=Neut|Number=Sing|PronType=Dem": {
        "det": {LEMMA: "det", "PronType": "Dem", "Number": "Sing", "Gender": "Neut"},
        "slikt": {LEMMA: "slik", "PronType": "Dem", "Number": "Sing", "Gender": "Neut"},
        "dette": {
            LEMMA: "dette",
            "PronType": "Dem",
            "Number": "Sing",
            "Gender": "Neut",
        },
    },
    "DET__Number=Plur|PronType=Dem": {
        "disse": {LEMMA: "disse", "PronType": "Dem", "Number": "Plur"},
        "andre": {LEMMA: "annen", "PronType": "Dem", "Number": "Plur"},
        "de": {LEMMA: "de", "PronType": "Dem", "Number": "Plur"},
        "slike": {LEMMA: "slik", "PronType": "Dem", "Number": "Plur"},
    },
    "DET__Definite=Ind|Gender=Masc|Number=Sing|PronType=Dem": {
        "annen": {LEMMA: "annen", "PronType": "Dem", "Number": "Sing", "Gender": "Masc"}
    },
    "DET__Definite=Ind|Gender=Fem|Number=Sing|PronType=Dem": {
        "annen": {LEMMA: "annen", "PronType": "Dem", "Number": "Sing", "Gender": "Fem"}
    },
    "DET__Definite=Ind|Gender=Neut|Number=Sing|PronType=Dem": {
        "annet": {LEMMA: "annen", "PronType": "Dem", "Number": "Sing", "Gender": "Neut"}
    },
    "DET__Case=Gen|Definite=Ind|Gender=Masc|Number=Sing|PronType=Dem": {
        "annens": {
            LEMMA: "annnen",
            "PronType": "Dem",
            "Number": "Sing",
            "Gender": "Masc",
            "Case": "Gen",
        }
    },
    "DET__Case=Gen|Number=Plur|PronType=Dem": {
        "andres": {LEMMA: "annen", "PronType": "Dem", "Number": "Plur", "Case": "Gen"}
    },
    "DET__Case=Gen|Gender=Fem|Number=Sing|PronType=Dem": {
        "dens": {
            LEMMA: "den",
            "PronType": "Dem",
            "Number": "Sing",
            "Gender": "Fem",
            "Case": "Gen",
        }
    },
    "DET__Case=Gen|Gender=Masc|Number=Sing|PronType=Dem": {
        "hvis": {
            LEMMA: "hvis",
            "PronType": "Dem",
            "Number": "Sing",
            "Gender": "Masc",
            "Case": "Gen",
        },
        "dens": {
            LEMMA: "den",
            "PronType": "Dem",
            "Number": "Sing",
            "Gender": "Masc",
            "Case": "Gen",
        },
    },
    "DET__Case=Gen|Gender=Neut|Number=Sing|PronType=Dem": {
        "dets": {
            LEMMA: "det",
            "PronType": "Dem",
            "Number": "Sing",
            "Gender": "Neut",
            "Case": "Gen",
        }
    },
    "DET__Case=Gen|Number=Plur": {
        "alles": {LEMMA: "all", "Number": "Plur", "Case": "Gen"}
    },
    "DET__Definite=Def|Number=Sing|PronType=Dem": {
        "andre": {LEMMA: "annen", "Number": "Sing", "PronType": "Dem"}
    },
    "DET__Definite=Def|PronType=Dem": {
        "samme": {LEMMA: "samme", "PronType": "Dem"},
        "forrige": {LEMMA: "forrige", "PronType": "Dem"},
        "neste": {LEMMA: "neste", "PronType": "Dem"},
    },
    "DET__Definite=Def": {"selve": {LEMMA: "selve"}, "selveste": {LEMMA: "selveste"}},
    "DET___": {"selv": {LEMMA: "selv"}, "endel": {LEMMA: "endel"}},
    "DET__Definite=Ind|Gender=Fem|Number=Sing": {
        "egen": {LEMMA: "egen", "Gender": "Fem", "Number": "Sing"}
    },
    "DET__Definite=Ind|Gender=Masc|Number=Sing": {
        "egen": {LEMMA: "egen", "Gender": "Masc", "Number": "Sing"}
    },
    "DET__Definite=Ind|Gender=Neut|Number=Sing": {
        "eget": {LEMMA: "egen", "Gender": "Neut", "Number": "Sing"}
    },
    # same wordform and pos (verb), have to specify the exact features in order to not mix them up
    "VERB__Mood=Ind|Tense=Pres|VerbForm=Fin": {
        "så": {LEMMA: "så", "VerbForm": "Fin", "Tense": "Pres", "Mood": "Ind"}
    },
    "VERB__Mood=Ind|Tense=Past|VerbForm=Fin": {
        "så": {LEMMA: "se", "VerbForm": "Fin", "Tense": "Past", "Mood": "Ind"}
    },
}

# copied from the English morph_rules.py
for tag, rules in MORPH_RULES.items():
    for key, attrs in dict(rules).items():
        rules[key.title()] = attrs

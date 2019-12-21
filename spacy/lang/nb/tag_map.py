# coding: utf8
from __future__ import unicode_literals

from ...symbols import POS, PUNCT, ADJ, CONJ, CCONJ, SCONJ, SYM, NUM, DET, ADV, ADP, X
from ...symbols import VERB, NOUN, PROPN, PART, INTJ, PRON, AUX


# Tags are a combination of POS and morphological features from a
# https://github.com/ltgoslo/norne developed by Schibsted, Nasjonalbiblioteket and LTG. The
# data format is .conllu and follows the Universal Dependencies annotation.
# (There are some annotation differences compared to this dataset:
# https://github.com/UniversalDependencies/UD_Norwegian-Bokmaal
# mainly in the way determiners and pronouns are tagged).
TAG_MAP = {
    "ADJ__Case=Gen|Definite=Def|Degree=Pos|Number=Sing": {
        "morph": "Case=Gen|Definite=Def|Degree=Pos|Number=Sing",
        POS: ADJ,
    },
    "ADJ__Case=Gen|Definite=Def|Number=Sing": {
        "morph": "Case=Gen|Definite=Def|Number=Sing",
        POS: ADJ,
    },
    "ADJ__Case=Gen|Definite=Ind|Degree=Pos|Gender=Neut|Number=Sing": {
        "morph": "Case=Gen|Definite=Ind|Degree=Pos|Gender=Neut|Number=Sing",
        POS: ADJ,
    },
    "ADJ__Case=Gen|Definite=Ind|Degree=Pos|Number=Sing": {
        "morph": "Case=Gen|Definite=Ind|Degree=Pos|Number=Sing",
        POS: ADJ,
    },
    "ADJ__Case=Gen|Degree=Cmp": {"morph": "Case=Gen|Degree=Cmp", POS: ADJ},
    "ADJ__Case=Gen|Degree=Pos|Number=Plur": {
        "morph": "Case=Gen|Degree=Pos|Number=Plur",
        POS: ADJ,
    },
    "ADJ__Definite=Def|Degree=Pos|Gender=Masc|Number=Sing": {
        "morph": "Definite=Def|Degree=Pos|Gender=Masc|Number=Sing",
        POS: ADJ,
    },
    "ADJ__Definite=Def|Degree=Pos|Number=Sing": {
        "morph": "Definite=Def|Degree=Pos|Number=Sing",
        POS: ADJ,
    },
    "ADJ__Definite=Def|Degree=Sup": {"morph": "Definite=Def|Degree=Sup", POS: ADJ},
    "ADJ__Definite=Def|Number=Sing": {"morph": "Definite=Def|Number=Sing", POS: ADJ},
    "ADJ__Definite=Ind|Degree=Pos": {"morph": "Definite=Ind|Degree=Pos", POS: ADJ},
    "ADJ__Definite=Ind|Degree=Pos|Gender=Masc|Number=Sing": {
        "morph": "Definite=Ind|Degree=Pos|Gender=Masc|Number=Sing",
        POS: ADJ,
    },
    "ADJ__Definite=Ind|Degree=Pos|Gender=Neut|Number=Sing": {
        "morph": "Definite=Ind|Degree=Pos|Gender=Neut|Number=Sing",
        POS: ADJ,
    },
    "ADJ__Definite=Ind|Degree=Pos|Number=Sing": {
        "morph": "Definite=Ind|Degree=Pos|Number=Sing",
        POS: ADJ,
    },
    "ADJ__Definite=Ind|Degree=Sup": {"morph": "Definite=Ind|Degree=Sup", POS: ADJ},
    "ADJ__Definite=Ind|Gender=Masc|Number=Sing": {
        "morph": "Definite=Ind|Gender=Masc|Number=Sing",
        POS: ADJ,
    },
    "ADJ__Definite=Ind|Gender=Neut|Number=Sing": {
        "morph": "Definite=Ind|Gender=Neut|Number=Sing",
        POS: ADJ,
    },
    "ADJ__Definite=Ind|Number=Sing": {"morph": "Definite=Ind|Number=Sing", POS: ADJ},
    "ADJ__Degree=Cmp": {"morph": "Degree=Cmp", POS: ADJ},
    "ADJ__Degree=Pos": {"morph": "Degree=Pos", POS: ADJ},
    "ADJ__Degree=Pos|Number=Plur": {"morph": "Degree=Pos|Number=Plur", POS: ADJ},
    "ADJ__Degree=Sup": {"morph": "Degree=Sup", POS: ADJ},
    "ADJ__Number=Plur": {"morph": "Number=Plur", POS: ADJ},
    "ADJ__Number=Plur|VerbForm=Part": {"morph": "Number=Plur|VerbForm=Part", POS: ADJ},
    "ADJ__Number=Sing": {"morph": "Number=Sing", POS: ADJ},
    "ADJ___": {"morph": "_", POS: ADJ},
    "ADP___": {"morph": "_", POS: ADP},
    "ADV___": {"morph": "_", POS: ADV},
    "ADV__Gender=Masc": {"morph": "Gender=Masc", POS: ADV},
    "AUX__Mood=Imp|VerbForm=Fin": {"morph": "Mood=Imp|VerbForm=Fin", POS: AUX},
    "AUX__Mood=Ind|Tense=Past|VerbForm=Fin": {
        "morph": "Mood=Ind|Tense=Past|VerbForm=Fin",
        POS: AUX,
    },
    "AUX__Mood=Ind|Tense=Pres|VerbForm=Fin": {
        "morph": "Mood=Ind|Tense=Pres|VerbForm=Fin",
        POS: AUX,
    },
    "AUX__Mood=Ind|Tense=Pres|VerbForm=Fin|Voice=Pass": {
        "morph": "Mood=Ind|Tense=Pres|VerbForm=Fin|Voice=Pass",
        POS: AUX,
    },
    "AUX__VerbForm=Inf": {"morph": "VerbForm=Inf", POS: AUX},
    "AUX__VerbForm=Inf|Voice=Pass": {"morph": "VerbForm=Inf|Voice=Pass", POS: AUX},
    "AUX__VerbForm=Part": {"morph": "VerbForm=Part", POS: AUX},
    "CONJ___": {"morph": "_", POS: CONJ},
    "DET__Case=Gen|Definite=Ind|Gender=Masc|Number=Sing|PronType=Dem": {
        "morph": "Case=Gen|Definite=Ind|Gender=Masc|Number=Sing|PronType=Dem",
        POS: DET,
    },
    "DET__Case=Gen|Gender=Fem|Number=Sing|PronType=Dem": {
        "morph": "Case=Gen|Gender=Fem|Number=Sing|PronType=Dem",
        POS: DET,
    },
    "DET__Case=Gen|Gender=Masc|Number=Sing": {
        "morph": "Case=Gen|Gender=Masc|Number=Sing",
        POS: DET,
    },
    "DET__Case=Gen|Gender=Masc|Number=Sing|PronType=Dem": {
        "morph": "Case=Gen|Gender=Masc|Number=Sing|PronType=Dem",
        POS: DET,
    },
    "DET__Case=Gen|Gender=Neut|Number=Sing|PronType=Dem": {
        "morph": "Case=Gen|Gender=Neut|Number=Sing|PronType=Dem",
        POS: DET,
    },
    "DET__Case=Gen|Number=Plur": {"morph": "Case=Gen|Number=Plur", POS: DET},
    "DET__Case=Gen|Number=Plur|PronType=Dem": {
        "morph": "Case=Gen|Number=Plur|PronType=Dem",
        POS: DET,
    },
    "DET__Definite=Def": {"morph": "Definite=Def", POS: DET},
    "DET__Definite=Def|Number=Sing|PronType=Dem": {
        "morph": "Definite=Def|Number=Sing|PronType=Dem",
        POS: DET,
    },
    "DET__Definite=Def|PronType=Dem": {"morph": "Definite=Def|PronType=Dem", POS: DET},
    "DET__Definite=Ind|Gender=Fem|Number=Sing": {
        "morph": "Definite=Ind|Gender=Fem|Number=Sing",
        POS: DET,
    },
    "DET__Definite=Ind|Gender=Fem|Number=Sing|PronType=Dem": {
        "morph": "Definite=Ind|Gender=Fem|Number=Sing|PronType=Dem",
        POS: DET,
    },
    "DET__Definite=Ind|Gender=Masc|Number=Sing": {
        "morph": "Definite=Ind|Gender=Masc|Number=Sing",
        POS: DET,
    },
    "DET__Definite=Ind|Gender=Masc|Number=Sing|PronType=Dem": {
        "morph": "Definite=Ind|Gender=Masc|Number=Sing|PronType=Dem",
        POS: DET,
    },
    "DET__Definite=Ind|Gender=Neut|Number=Sing": {
        "morph": "Definite=Ind|Gender=Neut|Number=Sing",
        POS: DET,
    },
    "DET__Definite=Ind|Gender=Neut|Number=Sing|PronType=Dem": {
        "morph": "Definite=Ind|Gender=Neut|Number=Sing|PronType=Dem",
        POS: DET,
    },
    "DET__Degree=Pos|Number=Plur": {"morph": "Degree=Pos|Number=Plur", POS: DET},
    "DET__Gender=Fem|Number=Sing": {"morph": "Gender=Fem|Number=Sing", POS: DET},
    "DET__Gender=Fem|Number=Sing|Poss=Yes": {
        "morph": "Gender=Fem|Number=Sing|Poss=Yes",
        POS: DET,
    },
    "DET__Gender=Fem|Number=Sing|PronType=Dem": {
        "morph": "Gender=Fem|Number=Sing|PronType=Dem",
        POS: DET,
    },
    "DET__Gender=Fem|Number=Sing|PronType=Int": {
        "morph": "Gender=Fem|Number=Sing|PronType=Int",
        POS: DET,
    },
    "DET__Gender=Masc|Number=Sing": {"morph": "Gender=Masc|Number=Sing", POS: DET},
    "DET__Gender=Masc|Number=Sing|Poss=Yes": {
        "morph": "Gender=Masc|Number=Sing|Poss=Yes",
        POS: DET,
    },
    "DET__Gender=Masc|Number=Sing|PronType=Dem": {
        "morph": "Gender=Masc|Number=Sing|PronType=Dem",
        POS: DET,
    },
    "DET__Gender=Masc|Number=Sing|PronType=Int": {
        "morph": "Gender=Masc|Number=Sing|PronType=Int",
        POS: DET,
    },
    "DET__Gender=Neut|Number=Sing": {"morph": "Gender=Neut|Number=Sing", POS: DET},
    "DET__Gender=Neut|Number=Sing|Poss=Yes": {
        "morph": "Gender=Neut|Number=Sing|Poss=Yes",
        POS: DET,
    },
    "DET__Gender=Neut|Number=Sing|PronType=Dem": {
        "morph": "Gender=Neut|Number=Sing|PronType=Dem",
        POS: DET,
    },
    "DET__Gender=Neut|Number=Sing|PronType=Int": {
        "morph": "Gender=Neut|Number=Sing|PronType=Int",
        POS: DET,
    },
    "DET__Number=Plur": {"morph": "Number=Plur", POS: DET},
    "DET__Number=Plur|Poss=Yes": {"morph": "Number=Plur|Poss=Yes", POS: DET},
    "DET__Number=Plur|Poss=Yes|PronType=Rcp": {
        "morph": "Number=Plur|Poss=Yes|PronType=Rcp",
        POS: DET,
    },
    "DET__Number=Plur|PronType=Dem": {"morph": "Number=Plur|PronType=Dem", POS: DET},
    "DET__Number=Plur|PronType=Int": {"morph": "Number=Plur|PronType=Int", POS: DET},
    "DET___": {"morph": "_", POS: DET},
    "INTJ___": {"morph": "_", POS: INTJ},
    "NOUN__Case=Gen": {"morph": "Case=Gen", POS: NOUN},
    "NOUN__Case=Gen|Definite=Def|Gender=Fem|Number=Plur": {
        "morph": "Case=Gen|Definite=Def|Gender=Fem|Number=Plur",
        POS: NOUN,
    },
    "NOUN__Case=Gen|Definite=Def|Gender=Fem|Number=Sing": {
        "morph": "Case=Gen|Definite=Def|Gender=Fem|Number=Sing",
        POS: NOUN,
    },
    "NOUN__Case=Gen|Definite=Def|Gender=Masc|Number=Plur": {
        "morph": "Case=Gen|Definite=Def|Gender=Masc|Number=Plur",
        POS: NOUN,
    },
    "NOUN__Case=Gen|Definite=Def|Gender=Masc|Number=Sing": {
        "morph": "Case=Gen|Definite=Def|Gender=Masc|Number=Sing",
        POS: NOUN,
    },
    "NOUN__Case=Gen|Definite=Def|Gender=Neut|Number=Plur": {
        "morph": "Case=Gen|Definite=Def|Gender=Neut|Number=Plur",
        POS: NOUN,
    },
    "NOUN__Case=Gen|Definite=Def|Gender=Neut|Number=Sing": {
        "morph": "Case=Gen|Definite=Def|Gender=Neut|Number=Sing",
        POS: NOUN,
    },
    "NOUN__Case=Gen|Definite=Ind|Gender=Fem|Number=Plur": {
        "morph": "Case=Gen|Definite=Ind|Gender=Fem|Number=Plur",
        POS: NOUN,
    },
    "NOUN__Case=Gen|Definite=Ind|Gender=Fem|Number=Sing": {
        "morph": "Case=Gen|Definite=Ind|Gender=Fem|Number=Sing",
        POS: NOUN,
    },
    "NOUN__Case=Gen|Definite=Ind|Gender=Masc|Number=Plur": {
        "morph": "Case=Gen|Definite=Ind|Gender=Masc|Number=Plur",
        POS: NOUN,
    },
    "NOUN__Case=Gen|Definite=Ind|Gender=Masc|Number=Sing": {
        "morph": "Case=Gen|Definite=Ind|Gender=Masc|Number=Sing",
        POS: NOUN,
    },
    "NOUN__Case=Gen|Definite=Ind|Gender=Neut|Number=Plur": {
        "morph": "Case=Gen|Definite=Ind|Gender=Neut|Number=Plur",
        POS: NOUN,
    },
    "NOUN__Case=Gen|Definite=Ind|Gender=Neut|Number=Sing": {
        "morph": "Case=Gen|Definite=Ind|Gender=Neut|Number=Sing",
        POS: NOUN,
    },
    "NOUN__Case=Gen|Gender=Fem": {"morph": "Case=Gen|Gender=Fem", POS: NOUN},
    "NOUN__Definite=Def,Ind|Gender=Masc|Number=Plur,Sing": {
        "morph": "Definite=Def",
        POS: NOUN,
    },
    "NOUN__Definite=Def,Ind|Gender=Masc|Number=Sing": {
        "morph": "Definite=Def",
        POS: NOUN,
    },
    "NOUN__Definite=Def,Ind|Gender=Neut|Number=Plur,Sing": {
        "morph": "Definite=Def",
        POS: NOUN,
    },
    "NOUN__Definite=Def|Gender=Fem|Number=Plur": {
        "morph": "Definite=Def|Gender=Fem|Number=Plur",
        POS: NOUN,
    },
    "NOUN__Definite=Def|Gender=Fem|Number=Sing": {
        "morph": "Definite=Def|Gender=Fem|Number=Sing",
        POS: NOUN,
    },
    "NOUN__Definite=Def|Gender=Masc|Number=Plur": {
        "morph": "Definite=Def|Gender=Masc|Number=Plur",
        POS: NOUN,
    },
    "NOUN__Definite=Def|Gender=Masc|Number=Sing": {
        "morph": "Definite=Def|Gender=Masc|Number=Sing",
        POS: NOUN,
    },
    "NOUN__Definite=Def|Gender=Neut|Number=Plur": {
        "morph": "Definite=Def|Gender=Neut|Number=Plur",
        POS: NOUN,
    },
    "NOUN__Definite=Def|Gender=Neut|Number=Sing": {
        "morph": "Definite=Def|Gender=Neut|Number=Sing",
        POS: NOUN,
    },
    "NOUN__Definite=Def|Number=Plur": {"morph": "Definite=Def|Number=Plur", POS: NOUN},
    "NOUN__Definite=Ind|Gender=Fem|Number=Plur": {
        "morph": "Definite=Ind|Gender=Fem|Number=Plur",
        POS: NOUN,
    },
    "NOUN__Definite=Ind|Gender=Fem|Number=Sing": {
        "morph": "Definite=Ind|Gender=Fem|Number=Sing",
        POS: NOUN,
    },
    "NOUN__Definite=Ind|Gender=Masc": {"morph": "Definite=Ind|Gender=Masc", POS: NOUN},
    "NOUN__Definite=Ind|Gender=Masc|Number=Plur": {
        "morph": "Definite=Ind|Gender=Masc|Number=Plur",
        POS: NOUN,
    },
    "NOUN__Definite=Ind|Gender=Masc|Number=Sing": {
        "morph": "Definite=Ind|Gender=Masc|Number=Sing",
        POS: NOUN,
    },
    "NOUN__Definite=Ind|Gender=Neut|Number=Plur": {
        "morph": "Definite=Ind|Gender=Neut|Number=Plur",
        POS: NOUN,
    },
    "NOUN__Definite=Ind|Gender=Neut|Number=Sing": {
        "morph": "Definite=Ind|Gender=Neut|Number=Sing",
        POS: NOUN,
    },
    "NOUN__Definite=Ind|Number=Plur": {"morph": "Definite=Ind|Number=Plur", POS: NOUN},
    "NOUN__Definite=Ind|Number=Sing": {"morph": "Definite=Ind|Number=Sing", POS: NOUN},
    "NOUN__Gender=Fem": {"morph": "Gender=Fem", POS: NOUN},
    "NOUN__Gender=Masc": {"morph": "Gender=Masc", POS: NOUN},
    "NOUN__Gender=Masc|Number=Sing": {"morph": "Gender=Masc|Number=Sing", POS: NOUN},
    "NOUN__Gender=Neut": {"morph": "Gender=Neut", POS: NOUN},
    "NOUN__Number=Plur": {"morph": "Number=Plur", POS: NOUN},
    "NOUN___": {"morph": "_", POS: NOUN},
    "NUM__Case=Gen|Number=Plur": {"morph": "Case=Gen|Number=Plur", POS: NUM},
    "NUM__Definite=Def": {"morph": "Definite=Def", POS: NUM},
    "NUM__Definite=Def|Number=Sing": {"morph": "Definite=Def|Number=Sing", POS: NUM},
    "NUM__Gender=Fem|Number=Sing": {"morph": "Gender=Fem|Number=Sing", POS: NUM},
    "NUM__Gender=Masc|Number=Sing": {"morph": "Gender=Masc|Number=Sing", POS: NUM},
    "NUM__Gender=Neut|Number=Sing": {"morph": "Gender=Neut|Number=Sing", POS: NUM},
    "NUM__Number=Plur": {"morph": "Number=Plur", POS: NUM},
    "NUM__Number=Sing": {"morph": "Number=Sing", POS: NUM},
    "NUM___": {"morph": "_", POS: NUM},
    "PART___": {"morph": "_", POS: PART},
    "PRON__Animacy=Anim|Case=Acc|Gender=Fem|Number=Sing|Person=3|PronType=Prs": {
        "morph": "Animacy=Anim|Case=Acc|Gender=Fem|Number=Sing|Person=",
        POS: PRON,
    },
    "PRON__Animacy=Anim|Case=Acc|Gender=Masc|Number=Sing|Person=3|PronType=Prs": {
        "morph": "Animacy=Anim|Case=Acc|Gender=Masc|Number=Sing|Person=",
        POS: PRON,
    },
    "PRON__Animacy=Anim|Case=Acc|Number=Plur|Person=1|PronType=Prs": {
        "morph": "Animacy=Anim|Case=Acc|Number=Plur|Person=",
        POS: PRON,
    },
    "PRON__Animacy=Anim|Case=Acc|Number=Plur|Person=2|PronType=Prs": {
        "morph": "Animacy=Anim|Case=Acc|Number=Plur|Person=",
        POS: PRON,
    },
    "PRON__Animacy=Anim|Case=Acc|Number=Sing|Person=1|PronType=Prs": {
        "morph": "Animacy=Anim|Case=Acc|Number=Sing|Person=",
        POS: PRON,
    },
    "PRON__Animacy=Anim|Case=Acc|Number=Sing|Person=2|PronType=Prs": {
        "morph": "Animacy=Anim|Case=Acc|Number=Sing|Person=",
        POS: PRON,
    },
    "PRON__Animacy=Anim|Case=Gen,Nom|Number=Sing|PronType=Prs": {
        "morph": "Animacy=Anim|Case=Gen",
        POS: PRON,
    },
    "PRON__Animacy=Anim|Case=Gen|Number=Sing|PronType=Prs": {
        "morph": "Animacy=Anim|Case=Gen|Number=Sing|PronType=Prs",
        POS: PRON,
    },
    "PRON__Animacy=Anim|Case=Nom|Gender=Fem|Number=Sing|Person=3|PronType=Prs": {
        "morph": "Animacy=Anim|Case=Nom|Gender=Fem|Number=Sing|Person=",
        POS: PRON,
    },
    "PRON__Animacy=Anim|Case=Nom|Gender=Masc|Number=Sing|Person=3|PronType=Prs": {
        "morph": "Animacy=Anim|Case=Nom|Gender=Masc|Number=Sing|Person=",
        POS: PRON,
    },
    "PRON__Animacy=Anim|Case=Nom|Number=Plur|Person=1|PronType=Prs": {
        "morph": "Animacy=Anim|Case=Nom|Number=Plur|Person=",
        POS: PRON,
    },
    "PRON__Animacy=Anim|Case=Nom|Number=Plur|Person=2|PronType=Prs": {
        "morph": "Animacy=Anim|Case=Nom|Number=Plur|Person=",
        POS: PRON,
    },
    "PRON__Animacy=Anim|Case=Nom|Number=Sing|Person=1|PronType=Prs": {
        "morph": "Animacy=Anim|Case=Nom|Number=Sing|Person=",
        POS: PRON,
    },
    "PRON__Animacy=Anim|Case=Nom|Number=Sing|Person=2|PronType=Prs": {
        "morph": "Animacy=Anim|Case=Nom|Number=Sing|Person=",
        POS: PRON,
    },
    "PRON__Animacy=Anim|Case=Nom|Number=Sing|PronType=Prs": {
        "morph": "Animacy=Anim|Case=Nom|Number=Sing|PronType=Prs",
        POS: PRON,
    },
    "PRON__Animacy=Anim|Number=Plur|PronType=Rcp": {
        "morph": "Animacy=Anim|Number=Plur|PronType=Rcp",
        POS: PRON,
    },
    "PRON__Animacy=Anim|Number=Sing|PronType=Prs": {
        "morph": "Animacy=Anim|Number=Sing|PronType=Prs",
        POS: PRON,
    },
    "PRON__Animacy=Anim|Poss=Yes|PronType=Int": {
        "morph": "Animacy=Anim|Poss=Yes|PronType=Int",
        POS: PRON,
    },
    "PRON__Animacy=Anim|PronType=Int": {
        "morph": "Animacy=Anim|PronType=Int",
        POS: PRON,
    },
    "PRON__Case=Acc|Number=Plur|Person=3|PronType=Prs": {
        "morph": "Case=Acc|Number=Plur|Person=",
        POS: PRON,
    },
    "PRON__Case=Acc|Reflex=Yes": {"morph": "Case=Acc|Reflex=Yes", POS: PRON},
    "PRON__Case=Nom|Number=Plur|Person=3|PronType=Prs": {
        "morph": "Case=Nom|Number=Plur|Person=",
        POS: PRON,
    },
    "PRON__Case=Gen|Number=Plur|Person=3|PronType=Prs": {
        "morph": "Case=Gen|Number=Plur|Person=3|PronType=Prs",
        POS: PRON,
    },
    "PRON__Gender=Fem,Masc|Number=Sing|Person=3|PronType=Prs": {
        "morph": "Gender=Fem",
        POS: PRON,
    },
    "PRON__Gender=Neut|Number=Sing|Person=3|PronType=Prs": {
        "morph": "Gender=Neut|Number=Sing|Person=",
        POS: PRON,
    },
    "PRON__Number=Plur|Person=3|PronType=Prs": {
        "morph": "Number=Plur|Person=",
        POS: PRON,
    },
    "PRON__Number=Sing": {"morph": "Number=Sing", POS: PRON},
    "PRON__PronType=Int": {"morph": "PronType=Int", POS: PRON},
    "PRON___": {"morph": "_", POS: PRON},
    "PROPN__Case=Gen": {"morph": "Case=Gen", POS: PROPN},
    "PROPN__Case=Gen|Gender=Fem": {"morph": "Case=Gen|Gender=Fem", POS: PROPN},
    "PROPN__Case=Gen|Gender=Masc": {"morph": "Case=Gen|Gender=Masc", POS: PROPN},
    "PROPN__Case=Gen|Gender=Neut": {"morph": "Case=Gen|Gender=Neut", POS: PROPN},
    "PROPN__Gender=Fem": {"morph": "Gender=Fem", POS: PROPN},
    "PROPN__Gender=Masc": {"morph": "Gender=Masc", POS: PROPN},
    "PROPN__Gender=Neut": {"morph": "Gender=Neut", POS: PROPN},
    "PROPN___": {"morph": "_", POS: PROPN},
    "PUNCT___": {"morph": "_", POS: PUNCT},
    "SCONJ___": {"morph": "_", POS: SCONJ},
    "SYM___": {"morph": "_", POS: SYM},
    "VERB__Definite=Ind|Number=Sing": {"morph": "Definite=Ind|Number=Sing", POS: VERB},
    "VERB__Mood=Imp|VerbForm=Fin": {"morph": "Mood=Imp|VerbForm=Fin", POS: VERB},
    "VERB__Mood=Ind|Tense=Past|VerbForm=Fin": {
        "morph": "Mood=Ind|Tense=Past|VerbForm=Fin",
        POS: VERB,
    },
    "VERB__Mood=Ind|Tense=Past|VerbForm=Fin|Voice=Pass": {
        "morph": "Mood=Ind|Tense=Past|VerbForm=Fin|Voice=Pass",
        POS: VERB,
    },
    "VERB__Mood=Ind|Tense=Pres|VerbForm=Fin": {
        "morph": "Mood=Ind|Tense=Pres|VerbForm=Fin",
        POS: VERB,
    },
    "VERB__Mood=Ind|Tense=Pres|VerbForm=Fin|Voice=Pass": {
        "morph": "Mood=Ind|Tense=Pres|VerbForm=Fin|Voice=Pass",
        POS: VERB,
    },
    "VERB__VerbForm=Inf": {"morph": "VerbForm=Inf", POS: VERB},
    "VERB__VerbForm=Inf|Voice=Pass": {"morph": "VerbForm=Inf|Voice=Pass", POS: VERB},
    "VERB__VerbForm=Part": {"morph": "VerbForm=Part", POS: VERB},
    "VERB___": {"morph": "_", POS: VERB},
    "X___": {"morph": "_", POS: X},
    "CCONJ___": {"morph": "_", POS: CCONJ},
    "ADJ__Abbr=Yes": {"morph": "Abbr=Yes", POS: ADJ},
    "ADJ__Abbr=Yes|Degree=Pos": {"morph": "Abbr=Yes|Degree=Pos", POS: ADJ},
    "ADJ__Case=Gen|Definite=Def|Number=Sing|VerbForm=Part": {
        "morph": "Case=Gen|Definite=Def|Number=Sing|VerbForm=Part",
        POS: ADJ,
    },
    "ADJ__Definite=Def|Number=Sing|VerbForm=Part": {
        "morph": "Definite=Def|Number=Sing|VerbForm=Part",
        POS: ADJ,
    },
    "ADJ__Definite=Ind|Gender=Masc|Number=Sing|VerbForm=Part": {
        "morph": "Definite=Ind|Gender=Masc|Number=Sing|VerbForm=Part",
        POS: ADJ,
    },
    "ADJ__Definite=Ind|Gender=Neut|Number=Sing|VerbForm=Part": {
        "morph": "Definite=Ind|Gender=Neut|Number=Sing|VerbForm=Part",
        POS: ADJ,
    },
    "ADJ__Definite=Ind|Number=Sing|VerbForm=Part": {
        "morph": "Definite=Ind|Number=Sing|VerbForm=Part",
        POS: ADJ,
    },
    "ADJ__Number=Sing|VerbForm=Part": {"morph": "Number=Sing|VerbForm=Part", POS: ADJ},
    "ADJ__VerbForm=Part": {"morph": "VerbForm=Part", POS: ADJ},
    "ADP__Abbr=Yes": {"morph": "Abbr=Yes", POS: ADP},
    "ADV__Abbr=Yes": {"morph": "Abbr=Yes", POS: ADV},
    "DET__Case=Gen|Gender=Masc|Number=Sing|PronType=Art": {
        "morph": "Case=Gen|Gender=Masc|Number=Sing|PronType=Art",
        POS: DET,
    },
    "DET__Case=Gen|Number=Plur|PronType=Tot": {
        "morph": "Case=Gen|Number=Plur|PronType=Tot",
        POS: DET,
    },
    "DET__Definite=Def|PronType=Prs": {"morph": "Definite=Def|PronType=Prs", POS: DET},
    "DET__Definite=Ind|Gender=Fem|Number=Sing|PronType=Prs": {
        "morph": "Definite=Ind|Gender=Fem|Number=Sing|PronType=Prs",
        POS: DET,
    },
    "DET__Definite=Ind|Gender=Masc|Number=Sing|PronType=Prs": {
        "morph": "Definite=Ind|Gender=Masc|Number=Sing|PronType=Prs",
        POS: DET,
    },
    "DET__Definite=Ind|Gender=Neut|Number=Sing|PronType=Prs": {
        "morph": "Definite=Ind|Gender=Neut|Number=Sing|PronType=Prs",
        POS: DET,
    },
    "DET__Gender=Fem|Number=Sing|PronType=Art": {
        "morph": "Gender=Fem|Number=Sing|PronType=Art",
        POS: DET,
    },
    "DET__Gender=Fem|Number=Sing|PronType=Ind": {
        "morph": "Gender=Fem|Number=Sing|PronType=Ind",
        POS: DET,
    },
    "DET__Gender=Fem|Number=Sing|PronType=Prs": {
        "morph": "Gender=Fem|Number=Sing|PronType=Prs",
        POS: DET,
    },
    "DET__Gender=Fem|Number=Sing|PronType=Tot": {
        "morph": "Gender=Fem|Number=Sing|PronType=Tot",
        POS: DET,
    },
    "DET__Gender=Masc|Number=Sing|Polarity=Neg|PronType=Neg": {
        "morph": "Gender=Masc|Number=Sing|Polarity=Neg|PronType=Neg",
        POS: DET,
    },
    "DET__Gender=Masc|Number=Sing|PronType=Art": {
        "morph": "Gender=Masc|Number=Sing|PronType=Art",
        POS: DET,
    },
    "DET__Gender=Masc|Number=Sing|PronType=Ind": {
        "morph": "Gender=Masc|Number=Sing|PronType=Ind",
        POS: DET,
    },
    "DET__Gender=Masc|Number=Sing|PronType=Tot": {
        "morph": "Gender=Masc|Number=Sing|PronType=Tot",
        POS: DET,
    },
    "DET__Gender=Neut|Number=Sing|Polarity=Neg|PronType=Neg": {
        "morph": "Gender=Neut|Number=Sing|Polarity=Neg|PronType=Neg",
        POS: DET,
    },
    "DET__Gender=Neut|Number=Sing|PronType=Art": {
        "morph": "Gender=Neut|Number=Sing|PronType=Art",
        POS: DET,
    },
    "DET__Gender=Neut|Number=Sing|PronType=Dem,Ind": {
        "morph": "Gender=Neut|Number=Sing|PronType=Dem,Ind",
        POS: DET,
    },
    "DET__Gender=Neut|Number=Sing|PronType=Ind": {
        "morph": "Gender=Neut|Number=Sing|PronType=Ind",
        POS: DET,
    },
    "DET__Gender=Neut|Number=Sing|PronType=Tot": {
        "morph": "Gender=Neut|Number=Sing|PronType=Tot",
        POS: DET,
    },
    "DET__Number=Plur|Polarity=Neg|PronType=Neg": {
        "morph": "Number=Plur|Polarity=Neg|PronType=Neg",
        POS: DET,
    },
    "DET__Number=Plur|PronType=Art": {"morph": "Number=Plur|PronType=Art", POS: DET},
    "DET__Number=Plur|PronType=Ind": {"morph": "Number=Plur|PronType=Ind", POS: DET},
    "DET__Number=Plur|PronType=Prs": {"morph": "Number=Plur|PronType=Prs", POS: DET},
    "DET__Number=Plur|PronType=Tot": {"morph": "Number=Plur|PronType=Tot", POS: DET},
    "DET__PronType=Ind": {"morph": "PronType=Ind", POS: DET},
    "DET__PronType=Prs": {"morph": "PronType=Prs", POS: DET},
    "NOUN__Abbr=Yes": {"morph": "Abbr=Yes", POS: NOUN},
    "NOUN__Abbr=Yes|Case=Gen": {"morph": "Abbr=Yes|Case=Gen", POS: NOUN},
    "NOUN__Abbr=Yes|Definite=Def,Ind|Gender=Masc|Number=Plur,Sing": {
        "morph": "Abbr=Yes|Definite=Def,Ind|Gender=Masc|Number=Plur,Sing",
        POS: NOUN,
    },
    "NOUN__Abbr=Yes|Definite=Def,Ind|Gender=Masc|Number=Sing": {
        "morph": "Abbr=Yes|Definite=Def,Ind|Gender=Masc|Number=Sing",
        POS: NOUN,
    },
    "NOUN__Abbr=Yes|Definite=Def,Ind|Gender=Neut|Number=Plur,Sing": {
        "morph": "Abbr=Yes|Definite=Def,Ind|Gender=Neut|Number=Plur,Sing",
        POS: NOUN,
    },
    "NOUN__Abbr=Yes|Gender=Masc": {"morph": "Abbr=Yes|Gender=Masc", POS: NOUN},
    "NUM__Case=Gen|Number=Plur|NumType=Card": {
        "morph": "Case=Gen|Number=Plur|NumType=Card",
        POS: NUM,
    },
    "NUM__Definite=Def|Number=Sing|NumType=Card": {
        "morph": "Definite=Def|Number=Sing|NumType=Card",
        POS: NUM,
    },
    "NUM__Definite=Def|NumType=Card": {"morph": "Definite=Def|NumType=Card", POS: NUM},
    "NUM__Gender=Fem|Number=Sing|NumType=Card": {
        "morph": "Gender=Fem|Number=Sing|NumType=Card",
        POS: NUM,
    },
    "NUM__Gender=Masc|Number=Sing|NumType=Card": {
        "morph": "Gender=Masc|Number=Sing|NumType=Card",
        POS: NUM,
    },
    "NUM__Gender=Neut|Number=Sing|NumType=Card": {
        "morph": "Gender=Neut|Number=Sing|NumType=Card",
        POS: NUM,
    },
    "NUM__Number=Plur|NumType=Card": {"morph": "Number=Plur|NumType=Card", POS: NUM},
    "NUM__Number=Sing|NumType=Card": {"morph": "Number=Sing|NumType=Card", POS: NUM},
    "NUM__NumType=Card": {"morph": "NumType=Card", POS: NUM},
    "PART__Polarity=Neg": {"morph": "Polarity=Neg", POS: PART},
    "PRON__Animacy=Hum|Case=Acc|Gender=Fem|Number=Sing|Person=3|PronType=Prs": {
        "morph": "Animacy=Hum|Case=Acc|Gender=Fem|Number=Sing|Person=3|PronType=Prs",
        POS: PRON,
    },
    "PRON__Animacy=Hum|Case=Acc|Gender=Masc|Number=Sing|Person=3|PronType=Prs": {
        "morph": "Animacy=Hum|Case=Acc|Gender=Masc|Number=Sing|Person=3|PronType=Prs",
        POS: PRON,
    },
    "PRON__Animacy=Hum|Case=Acc|Number=Plur|Person=1|PronType=Prs": {
        "morph": "Animacy=Hum|Case=Acc|Number=Plur|Person=1|PronType=Prs",
        POS: PRON,
    },
    "PRON__Animacy=Hum|Case=Acc|Number=Plur|Person=2|PronType=Prs": {
        "morph": "Animacy=Hum|Case=Acc|Number=Plur|Person=2|PronType=Prs",
        POS: PRON,
    },
    "PRON__Animacy=Hum|Case=Acc|Number=Sing|Person=1|PronType=Prs": {
        "morph": "Animacy=Hum|Case=Acc|Number=Sing|Person=1|PronType=Prs",
        POS: PRON,
    },
    "PRON__Animacy=Hum|Case=Acc|Number=Sing|Person=2|PronType=Prs": {
        "morph": "Animacy=Hum|Case=Acc|Number=Sing|Person=2|PronType=Prs",
        POS: PRON,
    },
    "PRON__Animacy=Hum|Case=Gen,Nom|Number=Sing|PronType=Art,Prs": {
        "morph": "Animacy=Hum|Case=Gen,Nom|Number=Sing|PronType=Art,Prs",
        POS: PRON,
    },
    "PRON__Animacy=Hum|Case=Gen|Number=Sing|PronType=Art,Prs": {
        "morph": "Animacy=Hum|Case=Gen|Number=Sing|PronType=Art,Prs",
        POS: PRON,
    },
    "PRON__Animacy=Hum|Case=Nom|Gender=Fem|Number=Sing|Person=3|PronType=Prs": {
        "morph": "Animacy=Hum|Case=Nom|Gender=Fem|Number=Sing|Person=3|PronType=Prs",
        POS: PRON,
    },
    "PRON__Animacy=Hum|Case=Nom|Gender=Masc|Number=Sing|Person=3|PronType=Prs": {
        "morph": "Animacy=Hum|Case=Nom|Gender=Masc|Number=Sing|Person=3|PronType=Prs",
        POS: PRON,
    },
    "PRON__Animacy=Hum|Case=Nom|Number=Plur|Person=1|PronType=Prs": {
        "morph": "Animacy=Hum|Case=Nom|Number=Plur|Person=1|PronType=Prs",
        POS: PRON,
    },
    "PRON__Animacy=Hum|Case=Nom|Number=Plur|Person=2|PronType=Prs": {
        "morph": "Animacy=Hum|Case=Nom|Number=Plur|Person=2|PronType=Prs",
        POS: PRON,
    },
    "PRON__Animacy=Hum|Case=Nom|Number=Sing|Person=1|PronType=Prs": {
        "morph": "Animacy=Hum|Case=Nom|Number=Sing|Person=1|PronType=Prs",
        POS: PRON,
    },
    "PRON__Animacy=Hum|Case=Nom|Number=Sing|Person=2|PronType=Prs": {
        "morph": "Animacy=Hum|Case=Nom|Number=Sing|Person=2|PronType=Prs",
        POS: PRON,
    },
    "PRON__Animacy=Hum|Case=Nom|Number=Sing|PronType=Prs": {
        "morph": "Animacy=Hum|Case=Nom|Number=Sing|PronType=Prs",
        POS: PRON,
    },
    "PRON__Animacy=Hum|Number=Plur|PronType=Rcp": {
        "morph": "Animacy=Hum|Number=Plur|PronType=Rcp",
        POS: PRON,
    },
    "PRON__Animacy=Hum|Number=Sing|PronType=Art,Prs": {
        "morph": "Animacy=Hum|Number=Sing|PronType=Art,Prs",
        POS: PRON,
    },
    "PRON__Animacy=Hum|Poss=Yes|PronType=Int": {
        "morph": "Animacy=Hum|Poss=Yes|PronType=Int",
        POS: PRON,
    },
    "PRON__Animacy=Hum|PronType=Int": {"morph": "Animacy=Hum|PronType=Int", POS: PRON},
    "PRON__Case=Acc|PronType=Prs|Reflex=Yes": {
        "morph": "Case=Acc|PronType=Prs|Reflex=Yes",
        POS: PRON,
    },
    "PRON__Gender=Fem,Masc|Number=Sing|Person=3|Polarity=Neg|PronType=Neg,Prs": {
        "morph": "Gender=Fem,Masc|Number=Sing|Person=3|Polarity=Neg|PronType=Neg,Prs",
        POS: PRON,
    },
    "PRON__Gender=Fem,Masc|Number=Sing|Person=3|PronType=Ind,Prs": {
        "morph": "Gender=Fem,Masc|Number=Sing|Person=3|PronType=Ind,Prs",
        POS: PRON,
    },
    "PRON__Gender=Fem,Masc|Number=Sing|Person=3|PronType=Prs,Tot": {
        "morph": "Gender=Fem,Masc|Number=Sing|Person=3|PronType=Prs,Tot",
        POS: PRON,
    },
    "PRON__Gender=Fem|Number=Sing|Poss=Yes|PronType=Prs": {
        "morph": "Gender=Fem|Number=Sing|Poss=Yes|PronType=Prs",
        POS: PRON,
    },
    "PRON__Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs": {
        "morph": "Gender=Masc|Number=Sing|Poss=Yes|PronType=Prs",
        POS: PRON,
    },
    "PRON__Gender=Neut|Number=Sing|Person=3|PronType=Ind,Prs": {
        "morph": "Gender=Neut|Number=Sing|Person=3|PronType=Ind,Prs",
        POS: PRON,
    },
    "PRON__Gender=Neut|Number=Sing|Poss=Yes|PronType=Prs": {
        "morph": "Gender=Neut|Number=Sing|Poss=Yes|PronType=Prs",
        POS: PRON,
    },
    "PRON__Number=Plur|Person=3|Polarity=Neg|PronType=Neg,Prs": {
        "morph": "Number=Plur|Person=3|Polarity=Neg|PronType=Neg,Prs",
        POS: PRON,
    },
    "PRON__Number=Plur|Person=3|PronType=Ind,Prs": {
        "morph": "Number=Plur|Person=3|PronType=Ind,Prs",
        POS: PRON,
    },
    "PRON__Number=Plur|Person=3|PronType=Prs,Tot": {
        "morph": "Number=Plur|Person=3|PronType=Prs,Tot",
        POS: PRON,
    },
    "PRON__Number=Plur|Poss=Yes|PronType=Prs": {
        "morph": "Number=Plur|Poss=Yes|PronType=Prs",
        POS: PRON,
    },
    "PRON__Number=Plur|Poss=Yes|PronType=Rcp": {
        "morph": "Number=Plur|Poss=Yes|PronType=Rcp",
        POS: PRON,
    },
    "PRON__Number=Sing|Polarity=Neg|PronType=Neg": {
        "morph": "Number=Sing|Polarity=Neg|PronType=Neg",
        POS: PRON,
    },
    "PRON__PronType=Prs": {"morph": "PronType=Prs", POS: PRON},
    "PRON__PronType=Rel": {"morph": "PronType=Rel", POS: PRON},
    "PROPN__Abbr=Yes": {"morph": "Abbr=Yes", POS: PROPN},
    "PROPN__Abbr=Yes|Case=Gen": {"morph": "Abbr=Yes|Case=Gen", POS: PROPN},
    "VERB__Abbr=Yes|Mood=Ind|Tense=Pres|VerbForm=Fin": {
        "morph": "Abbr=Yes|Mood=Ind|Tense=Pres|VerbForm=Fin",
        POS: VERB,
    },
    "VERB__Definite=Ind|Number=Sing|VerbForm=Part": {
        "morph": "Definite=Ind|Number=Sing|VerbForm=Part",
        POS: VERB,
    },
}

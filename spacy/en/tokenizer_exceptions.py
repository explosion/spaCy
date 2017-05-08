# coding: utf8
from __future__ import unicode_literals

from ..symbols import ORTH, LEMMA, TAG, NORM
from ..deprecated import PRON_LEMMA


_exc = {}
_exclude = ["Ill", "ill", "Its", "its", "Hell", "hell", "Shell", "shell",
               "Shed", "shed", "were", "Were", "Well", "well", "Whore", "whore"]


# Pronouns

for pron in ["i"]:
    for orth in [pron, pron.title()]:
        _exc[orth + "'m"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "'m", LEMMA: "be", TAG: "VBP", "tenspect": 1, "number": 1}]

        _exc[orth + "m"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "m", LEMMA: "be", TAG: "VBP", "tenspect": 1, "number": 1 }]

        _exc[orth + "'ma"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "'m", LEMMA: "be", NORM: "am"},
            {ORTH: "a", LEMMA: "going to", NORM: "gonna"}]

        _exc[orth + "ma"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "m", LEMMA: "be", NORM: "am"},
            {ORTH: "a", LEMMA: "going to", NORM: "gonna"}]


for pron in ["i", "you", "he", "she", "it", "we", "they"]:
    for orth in [pron, pron.title()]:
        _exc[orth + "'ll"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "'ll", LEMMA: "will", TAG: "MD"}]

        _exc[orth + "ll"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "ll", LEMMA: "will", TAG: "MD"}]

        _exc[orth + "'ll've"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "'ll", LEMMA: "will", TAG: "MD"},
            {ORTH: "'ve", LEMMA: "have", TAG: "VB"}]

        _exc[orth + "llve"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "ll", LEMMA: "will", TAG: "MD"},
            {ORTH: "ve", LEMMA: "have", TAG: "VB"}]

        _exc[orth + "'d"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "'d", LEMMA: "would", TAG: "MD"}]

        _exc[orth + "d"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "d", LEMMA: "would", TAG: "MD"}]

        _exc[orth + "'d've"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "'d", LEMMA: "would", TAG: "MD"},
            {ORTH: "'ve", LEMMA: "have", TAG: "VB"}]

        _exc[orth + "dve"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "d", LEMMA: "would", TAG: "MD"},
            {ORTH: "ve", LEMMA: "have", TAG: "VB"}]


for pron in ["i", "you", "we", "they"]:
    for orth in [pron, pron.title()]:
        _exc[orth + "'ve"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "'ve", LEMMA: "have", TAG: "VB"}]

        _exc[orth + "ve"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "ve", LEMMA: "have", TAG: "VB"}]


for pron in ["you", "we", "they"]:
    for orth in [pron, pron.title()]:
        _exc[orth + "'re"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "'re", LEMMA: "be", NORM: "are"}]

        _exc[orth + "re"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "re", LEMMA: "be", NORM: "are", TAG: "VBZ"}]


for pron in ["he", "she", "it"]:
    for orth in [pron, pron.title()]:
        _exc[orth + "'s"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "'s"}]

        _exc[orth + "s"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, TAG: "PRP"},
            {ORTH: "s"}]


# W-words, relative pronouns, prepositions etc.

for word in ["who", "what", "when", "where", "why", "how", "there", "that"]:
    for orth in [word, word.title()]:
        _exc[orth + "'s"] = [
            {ORTH: orth, LEMMA: word},
            {ORTH: "'s"}]

        _exc[orth + "s"] = [
            {ORTH: orth, LEMMA: word},
            {ORTH: "s"}]

        _exc[orth + "'ll"] = [
            {ORTH: orth, LEMMA: word},
            {ORTH: "'ll", LEMMA: "will", TAG: "MD"}]

        _exc[orth + "ll"] = [
            {ORTH: orth, LEMMA: word},
            {ORTH: "ll", LEMMA: "will", TAG: "MD"}]

        _exc[orth + "'ll've"] = [
            {ORTH: orth, LEMMA: word},
            {ORTH: "'ll", LEMMA: "will", TAG: "MD"},
            {ORTH: "'ve", LEMMA: "have", TAG: "VB"}]

        _exc[orth + "llve"] = [
            {ORTH: orth, LEMMA: word},
            {ORTH: "ll", LEMMA: "will", TAG: "MD"},
            {ORTH: "ve", LEMMA: "have", TAG: "VB"}]

        _exc[orth + "'re"] = [
            {ORTH: orth, LEMMA: word},
            {ORTH: "'re", LEMMA: "be", NORM: "are"}]

        _exc[orth + "re"] = [
            {ORTH: orth, LEMMA: word},
            {ORTH: "re", LEMMA: "be", NORM: "are"}]

        _exc[orth + "'ve"] = [
            {ORTH: orth},
            {ORTH: "'ve", LEMMA: "have", TAG: "VB"}]

        _exc[orth + "ve"] = [
            {ORTH: orth, LEMMA: word},
            {ORTH: "ve", LEMMA: "have", TAG: "VB"}]

        _exc[orth + "'d"] = [
            {ORTH: orth, LEMMA: word},
            {ORTH: "'d"}]

        _exc[orth + "d"] = [
            {ORTH: orth, LEMMA: word},
            {ORTH: "d"}]

        _exc[orth + "'d've"] = [
            {ORTH: orth, LEMMA: word},
            {ORTH: "'d", LEMMA: "would", TAG: "MD"},
            {ORTH: "'ve", LEMMA: "have", TAG: "VB"}]

        _exc[orth + "dve"] = [
            {ORTH: orth, LEMMA: word},
            {ORTH: "d", LEMMA: "would", TAG: "MD"},
            {ORTH: "ve", LEMMA: "have", TAG: "VB"}]


# Verbs

for verb_data in [
    {ORTH: "ca", LEMMA: "can", TAG: "MD"},
    {ORTH: "could", TAG: "MD"},
    {ORTH: "do", LEMMA: "do"},
    {ORTH: "does", LEMMA: "do"},
    {ORTH: "did", LEMMA: "do", TAG: "VBD"},
    {ORTH: "had", LEMMA: "have", TAG: "VBD"},
    {ORTH: "may", TAG: "MD"},
    {ORTH: "might", TAG: "MD"},
    {ORTH: "must", TAG: "MD"},
    {ORTH: "need"},
    {ORTH: "ought"},
    {ORTH: "sha", LEMMA: "shall", TAG: "MD"},
    {ORTH: "should", TAG: "MD"},
    {ORTH: "wo", LEMMA: "will", TAG: "MD"},
    {ORTH: "would", TAG: "MD"}]:
    verb_data_tc = dict(verb_data)
    verb_data_tc[ORTH] = verb_data_tc[ORTH].title()
    for data in [verb_data, verb_data_tc]:
        _exc[data[ORTH] + "n't"] = [
            dict(data),
            {ORTH: "n't", LEMMA: "not", TAG: "RB"}]

        _exc[data[ORTH] + "nt"] = [
            dict(data),
            {ORTH: "nt", LEMMA: "not", TAG: "RB"}]

        _exc[data[ORTH] + "n't've"] = [
            dict(data),
            {ORTH: "n't", LEMMA: "not", TAG: "RB"},
            {ORTH: "'ve", LEMMA: "have", TAG: "VB"}]

        _exc[data[ORTH] + "ntve"] = [
            dict(data),
            {ORTH: "nt", LEMMA: "not", TAG: "RB"},
            {ORTH: "ve", LEMMA: "have", TAG: "VB"}]


for verb_data in [
    {ORTH: "could", TAG: "MD"},
    {ORTH: "might"},
    {ORTH: "must"},
    {ORTH: "should"}]:
    verb_data_tc = dict(verb_data)
    verb_data_tc[ORTH] = verb_data_tc[ORTH].title()
    for data in [verb_data, verb_data_tc]:
        _exc[data[ORTH] + "'ve"] = [
            dict(data),
            {ORTH: "'ve", LEMMA: "have", TAG: "VB"}]

        _exc[data[ORTH] + "ve"] = [
            dict(data),
            {ORTH: "ve", LEMMA: "have", TAG: "VB"}]


for verb_data in [
    {ORTH: "ai", TAG: "VBP", "number": 2, LEMMA: "be"},
    {ORTH: "are", LEMMA: "be", TAG: "VBP", "number": 2},
    {ORTH: "is", LEMMA: "be", TAG: "VBZ"},
    {ORTH: "was", LEMMA: "be"},
    {ORTH: "were", LEMMA: "be"}]:
    verb_data_tc = dict(verb_data)
    verb_data_tc[ORTH] = verb_data_tc[ORTH].title()
    for data in [verb_data, verb_data_tc]:
        _exc[data[ORTH] + "n't"] = [
            dict(data),
            {ORTH: "n't", LEMMA: "not", TAG: "RB"}]

        _exc[data[ORTH] + "nt"] = [
            dict(data),
            {ORTH: "nt", LEMMA: "not", TAG: "RB"}]


# Other contractions with trailing apostrophe

for exc_data in [
    {ORTH: "doin", LEMMA: "do", NORM: "doing"},
    {ORTH: "goin", LEMMA: "go", NORM: "going"},
    {ORTH: "nothin", LEMMA: "nothing"},
    {ORTH: "nuthin", LEMMA: "nothing"},
    {ORTH: "ol", LEMMA: "old"},
    {ORTH: "somethin", LEMMA: "something"}]:
    exc_data_tc = dict(exc_data)
    exc_data_tc[ORTH] = exc_data_tc[ORTH].title()
    for data in [exc_data, exc_data_tc]:
        data_apos = dict(data)
        data_apos[ORTH] = data_apos[ORTH] + "'"
        _exc[data[ORTH]] = [dict(data)]
        _exc[data_apos[ORTH]] = [dict(data_apos)]


# Other contractions with leading apostrophe

for exc_data in [
    {ORTH: "cause", LEMMA: "because"},
    {ORTH: "em", LEMMA: PRON_LEMMA, NORM: "them"},
    {ORTH: "ll", LEMMA: "will"},
    {ORTH: "nuff", LEMMA: "enough"}]:
    exc_data_apos = dict(exc_data)
    exc_data_apos[ORTH] = "'" + exc_data_apos[ORTH]
    for data in [exc_data, exc_data_apos]:
        _exc[data[ORTH]] = [dict(data)]


# Times

for h in range(1, 12 + 1):
    hour = str(h)
    for period in ["a.m.", "am"]:
        _exc[hour+period] = [
            {ORTH: hour},
            {ORTH: period, LEMMA: "a.m."}]
    for period in ["p.m.", "pm"]:
        _exc[hour+period] = [
            {ORTH: hour},
            {ORTH: period, LEMMA: "p.m."}]


# Rest

_other_exc = {
    "y'all": [
        {ORTH: "y'", LEMMA: PRON_LEMMA, NORM: "you"},
        {ORTH: "all"}],

    "yall": [
        {ORTH: "y", LEMMA: PRON_LEMMA, NORM: "you"},
        {ORTH: "all"}],

    "how'd'y": [
        {ORTH: "how", LEMMA: "how"},
        {ORTH: "'d", LEMMA: "do"},
        {ORTH: "'y", LEMMA: PRON_LEMMA, NORM: "you"}],

    "How'd'y": [
        {ORTH: "How", LEMMA: "how"},
        {ORTH: "'d", LEMMA: "do"},
        {ORTH: "'y", LEMMA: PRON_LEMMA, NORM: "you"}],

    "not've": [
        {ORTH: "not", LEMMA: "not", TAG: "RB"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}],

    "notve": [
        {ORTH: "not", LEMMA: "not", TAG: "RB"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}],

    "Not've": [
        {ORTH: "Not", LEMMA: "not", TAG: "RB"},
        {ORTH: "'ve", LEMMA: "have", TAG: "VB"}],

    "Notve": [
        {ORTH: "Not", LEMMA: "not", TAG: "RB"},
        {ORTH: "ve", LEMMA: "have", TAG: "VB"}],

    "cannot": [
        {ORTH: "can", LEMMA: "can", TAG: "MD"},
        {ORTH: "not", LEMMA: "not", TAG: "RB"}],

    "Cannot": [
        {ORTH: "Can", LEMMA: "can", TAG: "MD"},
        {ORTH: "not", LEMMA: "not", TAG: "RB"}],

    "gonna": [
        {ORTH: "gon", LEMMA: "go", NORM: "going"},
        {ORTH: "na", LEMMA: "to"}],

    "Gonna": [
        {ORTH: "Gon", LEMMA: "go", NORM: "going"},
        {ORTH: "na", LEMMA: "to"}],

    "gotta": [
        {ORTH: "got"},
        {ORTH: "ta", LEMMA: "to"}],

    "Gotta": [
        {ORTH: "Got"},
        {ORTH: "ta", LEMMA: "to"}],

    "let's": [
        {ORTH: "let"},
        {ORTH: "'s", LEMMA: PRON_LEMMA, NORM: "us"}],

    "Let's": [
        {ORTH: "Let", LEMMA: "let"},
        {ORTH: "'s", LEMMA: PRON_LEMMA, NORM: "us"}]
}

_exc.update(_other_exc)


for exc_data in [
    {ORTH: "'S", LEMMA: "'s"},
    {ORTH: "'s", LEMMA: "'s"},
    {ORTH: "\u2018S", LEMMA: "'s"},
    {ORTH: "\u2018s", LEMMA: "'s"},
    {ORTH: "and/or", LEMMA: "and/or", TAG: "CC"},
    {ORTH: "'re", LEMMA: "be", NORM: "are"},
    {ORTH: "'Cause", LEMMA: "because"},
    {ORTH: "'cause", LEMMA: "because"},
    {ORTH: "ma'am", LEMMA: "madam"},
    {ORTH: "Ma'am", LEMMA: "madam"},
    {ORTH: "o'clock", LEMMA: "o'clock"},
    {ORTH: "O'clock", LEMMA: "o'clock"},

    {ORTH: "Mt.", LEMMA: "Mount"},
    {ORTH: "Ak.", LEMMA: "Alaska"},
    {ORTH: "Ala.", LEMMA: "Alabama"},
    {ORTH: "Apr.", LEMMA: "April"},
    {ORTH: "Ariz.", LEMMA: "Arizona"},
    {ORTH: "Ark.", LEMMA: "Arkansas"},
    {ORTH: "Aug.", LEMMA: "August"},
    {ORTH: "Calif.", LEMMA: "California"},
    {ORTH: "Colo.", LEMMA: "Colorado"},
    {ORTH: "Conn.", LEMMA: "Connecticut"},
    {ORTH: "Dec.", LEMMA: "December"},
    {ORTH: "Del.", LEMMA: "Delaware"},
    {ORTH: "Feb.", LEMMA: "February"},
    {ORTH: "Fla.", LEMMA: "Florida"},
    {ORTH: "Ga.", LEMMA: "Georgia"},
    {ORTH: "Ia.", LEMMA: "Iowa"},
    {ORTH: "Id.", LEMMA: "Idaho"},
    {ORTH: "Ill.", LEMMA: "Illinois"},
    {ORTH: "Ind.", LEMMA: "Indiana"},
    {ORTH: "Jan.", LEMMA: "January"},
    {ORTH: "Jul.", LEMMA: "July"},
    {ORTH: "Jun.", LEMMA: "June"},
    {ORTH: "Kan.", LEMMA: "Kansas"},
    {ORTH: "Kans.", LEMMA: "Kansas"},
    {ORTH: "Ky.", LEMMA: "Kentucky"},
    {ORTH: "La.", LEMMA: "Louisiana"},
    {ORTH: "Mar.", LEMMA: "March"},
    {ORTH: "Mass.", LEMMA: "Massachusetts"},
    {ORTH: "May.", LEMMA: "May"},
    {ORTH: "Mich.", LEMMA: "Michigan"},
    {ORTH: "Minn.", LEMMA: "Minnesota"},
    {ORTH: "Miss.", LEMMA: "Mississippi"},
    {ORTH: "N.C.", LEMMA: "North Carolina"},
    {ORTH: "N.D.", LEMMA: "North Dakota"},
    {ORTH: "N.H.", LEMMA: "New Hampshire"},
    {ORTH: "N.J.", LEMMA: "New Jersey"},
    {ORTH: "N.M.", LEMMA: "New Mexico"},
    {ORTH: "N.Y.", LEMMA: "New York"},
    {ORTH: "Neb.", LEMMA: "Nebraska"},
    {ORTH: "Nebr.", LEMMA: "Nebraska"},
    {ORTH: "Nev.", LEMMA: "Nevada"},
    {ORTH: "Nov.", LEMMA: "November"},
    {ORTH: "Oct.", LEMMA: "October"},
    {ORTH: "Okla.", LEMMA: "Oklahoma"},
    {ORTH: "Ore.", LEMMA: "Oregon"},
    {ORTH: "Pa.", LEMMA: "Pennsylvania"},
    {ORTH: "S.C.", LEMMA: "South Carolina"},
    {ORTH: "Sep.", LEMMA: "September"},
    {ORTH: "Sept.", LEMMA: "September"},
    {ORTH: "Tenn.", LEMMA: "Tennessee"},
    {ORTH: "Va.", LEMMA: "Virginia"},
    {ORTH: "Wash.", LEMMA: "Washington"},
    {ORTH: "Wis.", LEMMA: "Wisconsin"}]:
    _exc[exc_data[ORTH]] = [dict(exc_data)]


for orth in [
    "'d", "a.m.", "Adm.", "Bros.", "co.", "Co.", "Corp.", "D.C.", "Dr.", "e.g.",
    "E.g.", "E.G.", "Gen.", "Gov.", "i.e.", "I.e.", "I.E.", "Inc.", "Jr.",
    "Ltd.", "Md.", "Messrs.", "Mo.", "Mont.", "Mr.", "Mrs.", "Ms.", "p.m.",
    "Ph.D.", "Rep.", "Rev.", "Sen.", "St.", "vs."]:
    _exc[orth] = [{ORTH: orth}]


for string in _exclude:
    if string in _exc:
        _exc.pop(string)


TOKENIZER_EXCEPTIONS = dict(_exc)

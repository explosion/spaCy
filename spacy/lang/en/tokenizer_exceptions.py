# coding: utf8
from __future__ import unicode_literals

from ...symbols import ORTH, LEMMA, TAG, NORM, PRON_LEMMA


_exc = {}
_exclude = ["Ill", "ill", "Its", "its", "Hell", "hell", "Shell", "shell",
               "Shed", "shed", "were", "Were", "Well", "well", "Whore", "whore"]


# Pronouns

for pron in ["i"]:
    for orth in [pron, pron.title()]:
        _exc[orth + "'m"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, NORM: pron, TAG: "PRP"},
            {ORTH: "'m", LEMMA: "be", NORM: "am", TAG: "VBP", "tenspect": 1, "number": 1}]

        _exc[orth + "m"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, NORM: pron, TAG: "PRP"},
            {ORTH: "m", LEMMA: "be", TAG: "VBP", "tenspect": 1, "number": 1 }]

        _exc[orth + "'ma"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, NORM: pron, TAG: "PRP"},
            {ORTH: "'m", LEMMA: "be", NORM: "am"},
            {ORTH: "a", LEMMA: "going to", NORM: "gonna"}]

        _exc[orth + "ma"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, NORM: pron, TAG: "PRP"},
            {ORTH: "m", LEMMA: "be", NORM: "am"},
            {ORTH: "a", LEMMA: "going to", NORM: "gonna"}]


for pron in ["i", "you", "he", "she", "it", "we", "they"]:
    for orth in [pron, pron.title()]:
        _exc[orth + "'ll"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, NORM: pron, TAG: "PRP"},
            {ORTH: "'ll", LEMMA: "will", NORM: "will", TAG: "MD"}]

        _exc[orth + "ll"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, NORM: pron, TAG: "PRP"},
            {ORTH: "ll", LEMMA: "will", NORM: "will", TAG: "MD"}]

        _exc[orth + "'ll've"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, NORM: pron, TAG: "PRP"},
            {ORTH: "'ll", LEMMA: "will", NORM: "will", TAG: "MD"},
            {ORTH: "'ve", LEMMA: "have", NORM: "have", TAG: "VB"}]

        _exc[orth + "llve"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, NORM: pron, TAG: "PRP"},
            {ORTH: "ll", LEMMA: "will", NORM: "will", TAG: "MD"},
            {ORTH: "ve", LEMMA: "have", NORM: "have", TAG: "VB"}]

        _exc[orth + "'d"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, NORM: pron, TAG: "PRP"},
            {ORTH: "'d", LEMMA: "would", NORM: "would", TAG: "MD"}]

        _exc[orth + "d"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, NORM: pron, TAG: "PRP"},
            {ORTH: "d", LEMMA: "would", NORM: "would", TAG: "MD"}]

        _exc[orth + "'d've"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, NORM: pron, TAG: "PRP"},
            {ORTH: "'d", LEMMA: "would", NORM: "would", TAG: "MD"},
            {ORTH: "'ve", LEMMA: "have", NORM: "have", TAG: "VB"}]

        _exc[orth + "dve"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, NORM: pron, TAG: "PRP"},
            {ORTH: "d", LEMMA: "would", NORM: "would", TAG: "MD"},
            {ORTH: "ve", LEMMA: "have", NORM: "have", TAG: "VB"}]


for pron in ["i", "you", "we", "they"]:
    for orth in [pron, pron.title()]:
        _exc[orth + "'ve"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, NORM: pron, TAG: "PRP"},
            {ORTH: "'ve", LEMMA: "have", NORM: "have", TAG: "VB"}]

        _exc[orth + "ve"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, NORM: pron, TAG: "PRP"},
            {ORTH: "ve", LEMMA: "have", NORM: "have", TAG: "VB"}]


for pron in ["you", "we", "they"]:
    for orth in [pron, pron.title()]:
        _exc[orth + "'re"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, NORM: pron, TAG: "PRP"},
            {ORTH: "'re", LEMMA: "be", NORM: "are"}]

        _exc[orth + "re"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, NORM: pron, TAG: "PRP"},
            {ORTH: "re", LEMMA: "be", NORM: "are", TAG: "VBZ"}]


for pron in ["he", "she", "it"]:
    for orth in [pron, pron.title()]:
        _exc[orth + "'s"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, NORM: pron, TAG: "PRP"},
            {ORTH: "'s", NORM: "'s"}]

        _exc[orth + "s"] = [
            {ORTH: orth, LEMMA: PRON_LEMMA, NORM: pron, TAG: "PRP"},
            {ORTH: "s"}]


# W-words, relative pronouns, prepositions etc.

for word in ["who", "what", "when", "where", "why", "how", "there", "that"]:
    for orth in [word, word.title()]:
        _exc[orth + "'s"] = [
            {ORTH: orth, LEMMA: word, NORM: word},
            {ORTH: "'s", NORM: "'s"}]

        _exc[orth + "s"] = [
            {ORTH: orth, LEMMA: word, NORM: word},
            {ORTH: "s"}]

        _exc[orth + "'ll"] = [
            {ORTH: orth, LEMMA: word, NORM: word},
            {ORTH: "'ll", LEMMA: "will", NORM: "will", TAG: "MD"}]

        _exc[orth + "ll"] = [
            {ORTH: orth, LEMMA: word, NORM: word},
            {ORTH: "ll", LEMMA: "will", NORM: "will", TAG: "MD"}]

        _exc[orth + "'ll've"] = [
            {ORTH: orth, LEMMA: word, NORM: word},
            {ORTH: "'ll", LEMMA: "will", NORM: "will", TAG: "MD"},
            {ORTH: "'ve", LEMMA: "have", NORM: "have", TAG: "VB"}]

        _exc[orth + "llve"] = [
            {ORTH: orth, LEMMA: word, NORM: word},
            {ORTH: "ll", LEMMA: "will", NORM: "will", TAG: "MD"},
            {ORTH: "ve", LEMMA: "have", NORM: "have", TAG: "VB"}]

        _exc[orth + "'re"] = [
            {ORTH: orth, LEMMA: word, NORM: word},
            {ORTH: "'re", LEMMA: "be", NORM: "are"}]

        _exc[orth + "re"] = [
            {ORTH: orth, LEMMA: word, NORM: word},
            {ORTH: "re", LEMMA: "be", NORM: "are"}]

        _exc[orth + "'ve"] = [
            {ORTH: orth, LEMMA: word, NORM: word},
            {ORTH: "'ve", LEMMA: "have", TAG: "VB"}]

        _exc[orth + "ve"] = [
            {ORTH: orth, LEMMA: word},
            {ORTH: "ve", LEMMA: "have", NORM: "have", TAG: "VB"}]

        _exc[orth + "'d"] = [
            {ORTH: orth, LEMMA: word, NORM: word},
            {ORTH: "'d", NORM: "'d"}]

        _exc[orth + "d"] = [
            {ORTH: orth, LEMMA: word, NORM: word},
            {ORTH: "d"}]

        _exc[orth + "'d've"] = [
            {ORTH: orth, LEMMA: word, NORM: word},
            {ORTH: "'d", LEMMA: "would", NORM: "would", TAG: "MD"},
            {ORTH: "'ve", LEMMA: "have", NORM: "have", TAG: "VB"}]

        _exc[orth + "dve"] = [
            {ORTH: orth, LEMMA: word, NORM: word},
            {ORTH: "d", LEMMA: "would", NORM: "would", TAG: "MD"},
            {ORTH: "ve", LEMMA: "have", NORM: "have", TAG: "VB"}]


# Verbs

for verb_data in [
    {ORTH: "ca", LEMMA: "can", NORM: "can", TAG: "MD"},
    {ORTH: "could", NORM: "could", TAG: "MD"},
    {ORTH: "do", LEMMA: "do", NORM: "do"},
    {ORTH: "does", LEMMA: "do", NORM: "does"},
    {ORTH: "did", LEMMA: "do", NORM: "do", TAG: "VBD"},
    {ORTH: "had", LEMMA: "have", NORM: "have", TAG: "VBD"},
    {ORTH: "may", NORM: "may", TAG: "MD"},
    {ORTH: "might", NORM: "might", TAG: "MD"},
    {ORTH: "must", NORM: "must", TAG: "MD"},
    {ORTH: "need", NORM: "need"},
    {ORTH: "ought", NORM: "ought", TAG: "MD"},
    {ORTH: "sha", LEMMA: "shall", NORM: "shall", TAG: "MD"},
    {ORTH: "should", NORM: "should", TAG: "MD"},
    {ORTH: "wo", LEMMA: "will", NORM: "will", TAG: "MD"},
    {ORTH: "would", NORM: "would", TAG: "MD"}]:
    verb_data_tc = dict(verb_data)
    verb_data_tc[ORTH] = verb_data_tc[ORTH].title()
    for data in [verb_data, verb_data_tc]:
        _exc[data[ORTH] + "n't"] = [
            dict(data),
            {ORTH: "n't", LEMMA: "not", NORM: "not", TAG: "RB"}]

        _exc[data[ORTH] + "nt"] = [
            dict(data),
            {ORTH: "nt", LEMMA: "not", NORM: "not", TAG: "RB"}]

        _exc[data[ORTH] + "n't've"] = [
            dict(data),
            {ORTH: "n't", LEMMA: "not", NORM: "not", TAG: "RB"},
            {ORTH: "'ve", LEMMA: "have", NORM: "have", TAG: "VB"}]

        _exc[data[ORTH] + "ntve"] = [
            dict(data),
            {ORTH: "nt", LEMMA: "not", NORM: "not", TAG: "RB"},
            {ORTH: "ve", LEMMA: "have", NORM: "have", TAG: "VB"}]


for verb_data in [
    {ORTH: "could", NORM: "could", TAG: "MD"},
    {ORTH: "might", NORM: "might", TAG: "MD"},
    {ORTH: "must", NORM: "must", TAG: "MD"},
    {ORTH: "should", NORM: "should", TAG: "MD"},
    {ORTH: "would", NORM: "would", TAG: "MD"}]:
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
    {ORTH: "ai", LEMMA: "be", TAG: "VBP", "number": 2},
    {ORTH: "are", LEMMA: "be", NORM: "are", TAG: "VBP", "number": 2},
    {ORTH: "is", LEMMA: "be", NORM: "is", TAG: "VBZ"},
    {ORTH: "was", LEMMA: "be", NORM: "was"},
    {ORTH: "were", LEMMA: "be", NORM: "were"},
    {ORTH: "have", NORM: "have"},
    {ORTH: "has", LEMMA: "have", NORM: "has"},
    {ORTH: "dare", NORM: "dare"}]:
    verb_data_tc = dict(verb_data)
    verb_data_tc[ORTH] = verb_data_tc[ORTH].title()
    for data in [verb_data, verb_data_tc]:
        _exc[data[ORTH] + "n't"] = [
            dict(data),
            {ORTH: "n't", LEMMA: "not", NORM: "not", TAG: "RB"}]

        _exc[data[ORTH] + "nt"] = [
            dict(data),
            {ORTH: "nt", LEMMA: "not", NORM: "not", TAG: "RB"}]


# Other contractions with trailing apostrophe

for exc_data in [
    {ORTH: "doin", LEMMA: "do", NORM: "doing"},
    {ORTH: "goin", LEMMA: "go", NORM: "going"},
    {ORTH: "nothin", LEMMA: "nothing", NORM: "nothing"},
    {ORTH: "nuthin", LEMMA: "nothing", NORM: "nothing"},
    {ORTH: "ol", LEMMA: "old", NORM: "old"},
    {ORTH: "somethin", LEMMA: "something", NORM: "something"}]:
    exc_data_tc = dict(exc_data)
    exc_data_tc[ORTH] = exc_data_tc[ORTH].title()
    for data in [exc_data, exc_data_tc]:
        data_apos = dict(data)
        data_apos[ORTH] = data_apos[ORTH] + "'"
        _exc[data[ORTH]] = [dict(data)]
        _exc[data_apos[ORTH]] = [dict(data_apos)]


# Other contractions with leading apostrophe

for exc_data in [
    {ORTH: "cause", LEMMA: "because", NORM: "because"},
    {ORTH: "em", LEMMA: PRON_LEMMA, NORM: "them"},
    {ORTH: "ll", LEMMA: "will", NORM: "will"},
    {ORTH: "nuff", LEMMA: "enough", NORM: "enough"}]:
    exc_data_apos = dict(exc_data)
    exc_data_apos[ORTH] = "'" + exc_data_apos[ORTH]
    for data in [exc_data, exc_data_apos]:
        _exc[data[ORTH]] = [data]


# Times

for h in range(1, 12 + 1):
    for period in ["a.m.", "am"]:
        _exc["%d%s" % (h, period)] = [
            {ORTH: "%d" % h},
            {ORTH: period, LEMMA: "a.m.", NORM: "a.m."}]
    for period in ["p.m.", "pm"]:
        _exc["%d%s" % (h, period)] = [
            {ORTH: "%d" % h},
            {ORTH: period, LEMMA: "p.m.", NORM: "p.m."}]


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
        {ORTH: "How", LEMMA: "how", NORM: "how"},
        {ORTH: "'d", LEMMA: "do"},
        {ORTH: "'y", LEMMA: PRON_LEMMA, NORM: "you"}],

    "not've": [
        {ORTH: "not", LEMMA: "not", TAG: "RB"},
        {ORTH: "'ve", LEMMA: "have", NORM: "have", TAG: "VB"}],

    "notve": [
        {ORTH: "not", LEMMA: "not", TAG: "RB"},
        {ORTH: "ve", LEMMA: "have", NORM: "have", TAG: "VB"}],

    "Not've": [
        {ORTH: "Not", LEMMA: "not", NORM: "not", TAG: "RB"},
        {ORTH: "'ve", LEMMA: "have", NORM: "have", TAG: "VB"}],

    "Notve": [
        {ORTH: "Not", LEMMA: "not", NORM: "not", TAG: "RB"},
        {ORTH: "ve", LEMMA: "have", NORM: "have", TAG: "VB"}],

    "cannot": [
        {ORTH: "can", LEMMA: "can", TAG: "MD"},
        {ORTH: "not", LEMMA: "not", TAG: "RB"}],

    "Cannot": [
        {ORTH: "Can", LEMMA: "can", NORM: "can", TAG: "MD"},
        {ORTH: "not", LEMMA: "not", TAG: "RB"}],

    "gonna": [
        {ORTH: "gon", LEMMA: "go", NORM: "going"},
        {ORTH: "na", LEMMA: "to", NORM: "to"}],

    "Gonna": [
        {ORTH: "Gon", LEMMA: "go", NORM: "going"},
        {ORTH: "na", LEMMA: "to", NORM: "to"}],

    "gotta": [
        {ORTH: "got"},
        {ORTH: "ta", LEMMA: "to", NORM: "to"}],

    "Gotta": [
        {ORTH: "Got", NORM: "got"},
        {ORTH: "ta", LEMMA: "to", NORM: "to"}],

    "let's": [
        {ORTH: "let"},
        {ORTH: "'s", LEMMA: PRON_LEMMA, NORM: "us"}],

    "Let's": [
        {ORTH: "Let", LEMMA: "let", NORM: "let"},
        {ORTH: "'s", LEMMA: PRON_LEMMA, NORM: "us"}]
}

_exc.update(_other_exc)


for exc_data in [
    {ORTH: "'S", LEMMA: "'s", NORM: "'s"},
    {ORTH: "'s", LEMMA: "'s", NORM: "'s"},
    {ORTH: "\u2018S", LEMMA: "'s", NORM: "'s"},
    {ORTH: "\u2018s", LEMMA: "'s", NORM: "'s"},
    {ORTH: "and/or", LEMMA: "and/or", NORM: "and/or", TAG: "CC"},
    {ORTH: "w/o", LEMMA: "without", NORM: "without"},
    {ORTH: "'re", LEMMA: "be", NORM: "are"},
    {ORTH: "'Cause", LEMMA: "because", NORM: "because"},
    {ORTH: "'cause", LEMMA: "because", NORM: "because"},
    {ORTH: "'cos", LEMMA: "because", NORM: "because"},
    {ORTH: "'Cos", LEMMA: "because", NORM: "because"},
    {ORTH: "'coz", LEMMA: "because", NORM: "because"},
    {ORTH: "'Coz", LEMMA: "because", NORM: "because"},
    {ORTH: "'cuz", LEMMA: "because", NORM: "because"},
    {ORTH: "'Cuz", LEMMA: "because", NORM: "because"},
    {ORTH: "'bout", LEMMA: "about", NORM: "about"},
    {ORTH: "ma'am", LEMMA: "madam", NORM: "madam"},
    {ORTH: "Ma'am", LEMMA: "madam", NORM: "madam"},
    {ORTH: "o'clock", LEMMA: "o'clock", NORM: "o'clock"},
    {ORTH: "O'clock", LEMMA: "o'clock", NORM: "o'clock"},
    {ORTH: "lovin'", LEMMA: "love", NORM: "loving"},
    {ORTH: "Lovin'", LEMMA: "love", NORM: "loving"},
    {ORTH: "lovin", LEMMA: "love", NORM: "loving"},
    {ORTH: "Lovin", LEMMA: "love", NORM: "loving"},
    {ORTH: "havin'", LEMMA: "have", NORM: "having"},
    {ORTH: "Havin'", LEMMA: "have", NORM: "having"},
    {ORTH: "havin", LEMMA: "have", NORM: "having"},
    {ORTH: "Havin", LEMMA: "have", NORM: "having"},
    {ORTH: "doin'", LEMMA: "do", NORM: "doing"},
    {ORTH: "Doin'", LEMMA: "do", NORM: "doing"},
    {ORTH: "doin", LEMMA: "do", NORM: "doing"},
    {ORTH: "Doin", LEMMA: "do", NORM: "doing"},
    {ORTH: "goin'", LEMMA: "go", NORM: "going"},
    {ORTH: "Goin'", LEMMA: "go", NORM: "going"},
    {ORTH: "goin", LEMMA: "go", NORM: "going"},
    {ORTH: "Goin", LEMMA: "go", NORM: "going"},


    {ORTH: "Mt.", LEMMA: "Mount", NORM: "Mount"},
    {ORTH: "Ak.", LEMMA: "Alaska", NORM: "Alaska"},
    {ORTH: "Ala.", LEMMA: "Alabama", NORM: "Alabama"},
    {ORTH: "Apr.", LEMMA: "April", NORM: "April"},
    {ORTH: "Ariz.", LEMMA: "Arizona", NORM: "Arizona"},
    {ORTH: "Ark.", LEMMA: "Arkansas", NORM: "Arkansas"},
    {ORTH: "Aug.", LEMMA: "August", NORM: "August"},
    {ORTH: "Calif.", LEMMA: "California", NORM: "California"},
    {ORTH: "Colo.", LEMMA: "Colorado", NORM: "Colorado"},
    {ORTH: "Conn.", LEMMA: "Connecticut", NORM: "Connecticut"},
    {ORTH: "Dec.", LEMMA: "December", NORM: "December"},
    {ORTH: "Del.", LEMMA: "Delaware", NORM: "Delaware"},
    {ORTH: "Feb.", LEMMA: "February", NORM: "February"},
    {ORTH: "Fla.", LEMMA: "Florida", NORM: "Florida"},
    {ORTH: "Ga.", LEMMA: "Georgia", NORM: "Georgia"},
    {ORTH: "Ia.", LEMMA: "Iowa", NORM: "Iowa"},
    {ORTH: "Id.", LEMMA: "Idaho", NORM: "Idaho"},
    {ORTH: "Ill.", LEMMA: "Illinois", NORM: "Illinois"},
    {ORTH: "Ind.", LEMMA: "Indiana", NORM: "Indiana"},
    {ORTH: "Jan.", LEMMA: "January", NORM: "January"},
    {ORTH: "Jul.", LEMMA: "July", NORM: "July"},
    {ORTH: "Jun.", LEMMA: "June", NORM: "June"},
    {ORTH: "Kan.", LEMMA: "Kansas", NORM: "Kansas"},
    {ORTH: "Kans.", LEMMA: "Kansas", NORM: "Kansas"},
    {ORTH: "Ky.", LEMMA: "Kentucky", NORM: "Kentucky"},
    {ORTH: "La.", LEMMA: "Louisiana", NORM: "Louisiana"},
    {ORTH: "Mar.", LEMMA: "March", NORM: "March"},
    {ORTH: "Mass.", LEMMA: "Massachusetts", NORM: "Massachusetts"},
    {ORTH: "May.", LEMMA: "May", NORM: "May"},
    {ORTH: "Mich.", LEMMA: "Michigan", NORM: "Michigan"},
    {ORTH: "Minn.", LEMMA: "Minnesota", NORM: "Minnesota"},
    {ORTH: "Miss.", LEMMA: "Mississippi", NORM: "Mississippi"},
    {ORTH: "N.C.", LEMMA: "North Carolina", NORM: "North Carolina"},
    {ORTH: "N.D.", LEMMA: "North Dakota", NORM: "North Dakota"},
    {ORTH: "N.H.", LEMMA: "New Hampshire", NORM: "New Hampshire"},
    {ORTH: "N.J.", LEMMA: "New Jersey", NORM: "New Jersey"},
    {ORTH: "N.M.", LEMMA: "New Mexico", NORM: "New Mexico"},
    {ORTH: "N.Y.", LEMMA: "New York", NORM: "New York"},
    {ORTH: "Neb.", LEMMA: "Nebraska", NORM: "Nebraska"},
    {ORTH: "Nebr.", LEMMA: "Nebraska", NORM: "Nebraska"},
    {ORTH: "Nev.", LEMMA: "Nevada", NORM: "Nevada"},
    {ORTH: "Nov.", LEMMA: "November", NORM: "November"},
    {ORTH: "Oct.", LEMMA: "October", NORM: "October"},
    {ORTH: "Okla.", LEMMA: "Oklahoma", NORM: "Oklahoma"},
    {ORTH: "Ore.", LEMMA: "Oregon", NORM: "Oregon"},
    {ORTH: "Pa.", LEMMA: "Pennsylvania", NORM: "Pennsylvania"},
    {ORTH: "S.C.", LEMMA: "South Carolina", NORM: "South Carolina"},
    {ORTH: "Sep.", LEMMA: "September", NORM: "September"},
    {ORTH: "Sept.", LEMMA: "September", NORM: "September"},
    {ORTH: "Tenn.", LEMMA: "Tennessee", NORM: "Tennessee"},
    {ORTH: "Va.", LEMMA: "Virginia", NORM: "Virginia"},
    {ORTH: "Wash.", LEMMA: "Washington", NORM: "Washington"},
    {ORTH: "Wis.", LEMMA: "Wisconsin", NORM: "Wisconsin"}]:
    _exc[exc_data[ORTH]] = [exc_data]


for orth in [
    "'d", "a.m.", "Adm.", "Bros.", "co.", "Co.", "Corp.", "D.C.", "Dr.", "e.g.",
    "E.g.", "E.G.", "Gen.", "Gov.", "i.e.", "I.e.", "I.E.", "Inc.", "Jr.",
    "Ltd.", "Md.", "Messrs.", "Mo.", "Mont.", "Mr.", "Mrs.", "Ms.", "p.m.",
    "Ph.D.", "Rep.", "Rev.", "Sen.", "St.", "vs."]:
    _exc[orth] = [{ORTH: orth}]


for string in _exclude:
    if string in _exc:
        _exc.pop(string)


TOKENIZER_EXCEPTIONS = _exc

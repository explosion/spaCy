# -#- coding: utf-8 -*-
import json

contractions = {"n't", "'nt", "not", "'ve", "'d", "'ll", "'s", "'m", "'ma", "'re"}

# contains the lemmas, parts of speech, number, and tenspect of
# potential tokens generated after splitting contractions off
token_properties = { 

            "ai": {"L": "be", "pos": "VBP", "number": 2},
            "are": {"L": "be", "pos": "VBP", "number": 2},
            "ca": {"L": "can", "pos": "MD"},
            "can": {"L": "can", "pos": "MD"},
            "could": {"pos": "MD", "L": "could"},
            "'d": {"L": "would", "pos": "MD"},
            "did": {"L": "do", "pos": "VBD"},
            "do": {"L": "do"},
            "does": {"L": "do", "pos": "VBZ"},
            "had": {"L": "have", "pos": "VBD"},
            "has": {"L": "have", "pos": "VBZ"},
            "have": {"pos": "VB"},
            "he": {"L": "-PRON-", "pos": "PRP"},
            "how": {},
            "i": {"L": "-PRON-", "pos": "PRP"},
            "is": {"L": "be", "pos": "VBZ"},
            "it": {"L": "-PRON-", "pos": "PRP"},
            "'ll": {"L": "will", "pos": "MD"},
            "'m": {"L": "be", "pos": "VBP", "number": 1, "tenspect": 1},
            "'ma": {},
            "might": {},
            "must": {},
            "need": {}, 
            "not": {"L": "not", "pos": "RB"},
            "'nt": {"L": "not", "pos": "RB"},
            "n't": {"L": "not", "pos": "RB"},
            "'re": {"L": "be", "pos": "VBZ"},
            "'s": {},                                       # no POS or lemma for s?
            "sha": {"L": "shall", "pos": "MD"},
            "she": {"L": "-PRON-", "pos": "PRP"},
            "should": {},
            "that": {},
            "there": {},
            "they": {"L": "-PRON-", "pos": "PRP"},
            "was": {},
            "we": {"L": "-PRON-", "pos": "PRP"},
            "were": {},
            "what": {},
            "when": {},
            "where": {},
            "who": {},
            "why": {},
            "wo": {},
            "would": {},
            "you": {"L": "-PRON-", "pos": "PRP"},
            "'ve": {"L": "have", "pos": "VB"}
}

# contains starting tokens with their potential contractions
# each potential contraction has a list of exceptions
    # lower - don't generate the lowercase version
    # upper - don't generate the uppercase version
    # contrLower - don't generate the lowercase version with apostrophe (') removed
    # contrUpper - dont' generate the uppercase version with apostrophe (') removed
# for example, we don't want to create the word "hell" or "Hell" from "he" + "'ll" so 
# we add "contrLower" and "contrUpper" to the exceptions list
starting_tokens = {

                "ai": {"n't": []}, 
                "are": {"n't": []}, 
                "ca": {"n't": []},
                "can": {"not": []},
                "could": {"'ve": [], "n't": [], "n't've": []},
                "did": {"n't": []},
                "does": {"n't": []},
                "do": {"n't": []},
                "had": {"n't": [], "n't've": []},
                "has": {"n't": []},
                "have": {"n't": []},
                "he": {"'d": [], "'d've": [], "'ll": ["contrLower", "contrUpper"], "'s": []},
                "how": {"'d": [], "'ll": [], "'s": []},
                "i": {"'d": ["contrLower", "contrUpper"], "'d've": [], "'ll": ["contrLower", "contrUpper"], "'m": [], "'ma": [], "'ve": []},
                "is": {"n't": []},
                "it": {"'d": [], "'d've": [], "'ll": [], "'s": ["contrLower", "contrUpper"]},
                "might": {"n't": [], "n't've": [], "'ve": []},
                "must": {"n't": [], "'ve": []},
                "need": {"n't": []},
                "not": {"'ve": []},
                "sha": {"n't": []},
                "she": {"'d": ["contrLower", "contrUpper"], "'d've": [], "'ll": ["contrLower", "contrUpper"], "'s": []},
                "should": {"'ve": [], "n't": [], "n't've": []},
                "that": {"'s": []},
                "there": {"'d": [], "'d've": [], "'s": ["contrLower", "contrUpper"], "'ll": []},
                "they": {"'d": [], "'d've": [], "'ll": [], "'re": [], "'ve": []},
                "was": {"n't": []},
                "we": {"'d": ["contrLower", "contrUpper"], "'d've": [], "'ll": ["contrLower", "contrUpper"], "'re": ["contrLower", "contrUpper"], "'ve": []},
                "were": {"n't": []},
                "what": {"'ll": [], "'re": [], "'s": [], "'ve": []},
                "when": {"'s": []},
                "where": {"'d": [], "'s": [], "'ve": []},
                "who": {"'d": [], "'ll": [], "'re": ["contrLower", "contrUpper"], "'s": [], "'ve": []},
                "why": {"'ll": [], "'re": [], "'s": []},
                "wo": {"n't": []},
                "would": {"'ve": [], "n't": [], "n't've": []},
                "you": {"'d": [], "'d've": [], "'ll": [], "'re": [], "'ve": []}

                }

# other specials that don't really have contractions
# so they are hardcoded
hardcoded_specials = {
                "let's": [{"F": "let"}, {"F": "'s", "L": "us"}],
                "Let's": [{"F": "Let"}, {"F": "'s", "L": "us"}],

                "'s":  [{"F": "'s", "L": "'s"}],

                "'S":  [{"F": "'S", "L": "'s"}],
                u"\u2018s": [{"F": u"\u2018s", "L": "'s"}],
                u"\u2018S": [{"F": u"\u2018S", "L": "'s"}],

                "'em": [{"F": "'em"}],

                "'ol": [{"F": "'ol"}],

                "vs.": [{"F": "vs."}],

                "Ms.": [{"F": "Ms."}],
                "Mr.": [{"F": "Mr."}],
                "Dr.": [{"F": "Dr."}],
                "Mrs.": [{"F": "Mrs."}],
                "Messrs.": [{"F": "Messrs."}],
                "Gov.": [{"F": "Gov."}],
                "Gen.": [{"F": "Gen."}],

                "Mt.": [{"F": "Mt.", "L": "Mount"}],

                "''": [{"F": "''"}],

                "—": [{"F": "—", "L": "--", "pos": ":"}],

                "Corp.": [{"F": "Corp."}],
                "Inc.": [{"F": "Inc."}],
                "Co.": [{"F": "Co."}],
                "co.": [{"F": "co."}],
                "Ltd.": [{"F": "Ltd."}],
                "Bros.": [{"F": "Bros."}],

                "Rep.": [{"F": "Rep."}],
                "Sen.": [{"F": "Sen."}],
                "Jr.": [{"F": "Jr."}],
                "Rev.": [{"F": "Rev."}],
                "Adm.": [{"F": "Adm."}],
                "St.": [{"F": "St."}],

                "a.m.": [{"F": "a.m."}],
                "p.m.": [{"F": "p.m."}],

                "1a.m.": [{"F": "1"}, {"F": "a.m."}],
                "2a.m.": [{"F": "2"}, {"F": "a.m."}],
                "3a.m.": [{"F": "3"}, {"F": "a.m."}],
                "4a.m.": [{"F": "4"}, {"F": "a.m."}],
                "5a.m.": [{"F": "5"}, {"F": "a.m."}],
                "6a.m.": [{"F": "6"}, {"F": "a.m."}],
                "7a.m.": [{"F": "7"}, {"F": "a.m."}],
                "8a.m.": [{"F": "8"}, {"F": "a.m."}],
                "9a.m.": [{"F": "9"}, {"F": "a.m."}],
                "10a.m.": [{"F": "10"}, {"F": "a.m."}],
                "11a.m.": [{"F": "11"}, {"F": "a.m."}],
                "12a.m.": [{"F": "12"}, {"F": "a.m."}],
                "1am": [{"F": "1"}, {"F": "am", "L": "a.m."}],
                "2am": [{"F": "2"}, {"F": "am", "L": "a.m."}],
                "3am": [{"F": "3"}, {"F": "am", "L": "a.m."}],
                "4am": [{"F": "4"}, {"F": "am", "L": "a.m."}],
                "5am": [{"F": "5"}, {"F": "am", "L": "a.m."}],
                "6am": [{"F": "6"}, {"F": "am", "L": "a.m."}],
                "7am": [{"F": "7"}, {"F": "am", "L": "a.m."}],
                "8am": [{"F": "8"}, {"F": "am", "L": "a.m."}],
                "9am": [{"F": "9"}, {"F": "am", "L": "a.m."}],
                "10am": [{"F": "10"}, {"F": "am", "L": "a.m."}],
                "11am": [{"F": "11"}, {"F": "am", "L": "a.m."}],
                "12am": [{"F": "12"}, {"F": "am", "L": "a.m."}],


                "p.m.": [{"F": "p.m."}],
                "1p.m.": [{"F": "1"}, {"F": "p.m."}],
                "2p.m.": [{"F": "2"}, {"F": "p.m."}],
                "3p.m.": [{"F": "3"}, {"F": "p.m."}],
                "4p.m.": [{"F": "4"}, {"F": "p.m."}],
                "5p.m.": [{"F": "5"}, {"F": "p.m."}],
                "6p.m.": [{"F": "6"}, {"F": "p.m."}],
                "7p.m.": [{"F": "7"}, {"F": "p.m."}],
                "8p.m.": [{"F": "8"}, {"F": "p.m."}],
                "9p.m.": [{"F": "9"}, {"F": "p.m."}],
                "10p.m.": [{"F": "10"}, {"F": "p.m."}],
                "11p.m.": [{"F": "11"}, {"F": "p.m."}],
                "12p.m.": [{"F": "12"}, {"F": "p.m."}],
                "1pm": [{"F": "1"}, {"F": "pm", "L": "p.m."}],
                "2pm": [{"F": "2"}, {"F": "pm", "L": "p.m."}],
                "3pm": [{"F": "3"}, {"F": "pm", "L": "p.m."}],
                "4pm": [{"F": "4"}, {"F": "pm", "L": "p.m."}],
                "5pm": [{"F": "5"}, {"F": "pm", "L": "p.m."}],
                "6pm": [{"F": "6"}, {"F": "pm", "L": "p.m."}],
                "7pm": [{"F": "7"}, {"F": "pm", "L": "p.m."}],
                "8pm": [{"F": "8"}, {"F": "pm", "L": "p.m."}],
                "9pm": [{"F": "9"}, {"F": "pm", "L": "p.m."}],
                "10pm": [{"F": "10"}, {"F": "pm", "L": "p.m."}],
                "11pm": [{"F": "11"}, {"F": "pm", "L": "p.m."}],
                "12pm": [{"F": "12"}, {"F": "pm", "L": "p.m."}],

                "Jan.": [{"F": "Jan."}],
                "Feb.": [{"F": "Feb."}],
                "Mar.": [{"F": "Mar."}],
                "Apr.": [{"F": "Apr."}],
                "May.": [{"F": "May."}],
                "Jun.": [{"F": "Jun."}],
                "Jul.": [{"F": "Jul."}],
                "Aug.": [{"F": "Aug."}],
                "Sep.": [{"F": "Sep."}],
                "Sept.": [{"F": "Sept."}],
                "Oct.": [{"F": "Oct."}],
                "Nov.": [{"F": "Nov."}],
                "Dec.": [{"F": "Dec."}],

                "Ala.": [{"F": "Ala."}],
                "Ariz.": [{"F": "Ariz."}],
                "Ark.": [{"F":  "Ark."}],
                "Calif.": [{"F": "Calif."}],
                "Colo.": [{"F": "Colo."}],
                "Conn.": [{"F": "Conn."}],
                "Del.": [{"F":  "Del."}],
                "D.C.": [{"F": "D.C."}],
                "Fla.": [{"F":  "Fla."}],
                "Ga.": [{"F": "Ga."}],
                "Ill.": [{"F": "Ill."}],
                "Ind.": [{"F": "Ind."}],
                "Kans.": [{"F": "Kans."}],
                "Kan.": [{"F": "Kan."}],
                "Ky.": [{"F": "Ky."}],
                "La.": [{"F": "La."}],
                "Md.": [{"F": "Md."}],
                "Mass.": [{"F": "Mass."}],
                "Mich.": [{"F": "Mich."}],
                "Minn.": [{"F": "Minn."}],
                "Miss.": [{"F": "Miss."}],
                "Mo.": [{"F": "Mo."}],
                "Mont.": [{"F": "Mont."}],
                "Nebr.": [{"F": "Nebr."}],
                "Neb.": [{"F": "Neb."}],
                "Nev.": [{"F":  "Nev."}],
                "N.H.": [{"F": "N.H."}],
                "N.J.": [{"F": "N.J."}],
                "N.M.": [{"F": "N.M."}],
                "N.Y.": [{"F": "N.Y."}],
                "N.C.": [{"F": "N.C."}],
                "N.D.": [{"F": "N.D."}],
                "Okla.": [{"F": "Okla."}],
                "Ore.": [{"F": "Ore."}],
                "Pa.": [{"F": "Pa."}],
                "Tenn.": [{"F": "Tenn."}],
                "Va.": [{"F": "Va."}],
                "Wash.": [{"F": "Wash."}],
                "Wis.": [{"F": "Wis."}],

                ":)":  [{"F": ":)"}],
                "<3":  [{"F": "<3"}],
                ";)":  [{"F": ";)"}],
                "(:":  [{"F": "(:"}],
                ":(":  [{"F": ":("}],
                "-_-": [{"F": "-_-"}],
                "=)":  [{"F": "=)"}],
                ":/":  [{"F": ":/"}],
                ":>":  [{"F": ":>"}],
                ";-)": [{"F": ";-)"}],
                ":Y":  [{"F": ":Y"}],
                ":P":  [{"F": ":P"}],
                ":-P": [{"F": ":-P"}],
                ":3":  [{"F": ":3"}],
                "=3":  [{"F": "=3"}],
                "xD":  [{"F": "xD"}],
                "^_^": [{"F": "^_^"}],
                "=]":  [{"F": "=]"}],
                "=D":  [{"F": "=D"}],
                "<333":    [{"F": "<333"}],
                ":))": [{"F": ":))"}],
                ":0":  [{"F": ":0"}],
                "-__-":    [{"F": "-__-"}],
                "xDD": [{"F": "xDD"}],
                "o_o": [{"F": "o_o"}],
                "o_O": [{"F": "o_O"}],
                "V_V": [{"F": "V_V"}],
                "=[[": [{"F": "=[["}],
                "<33": [{"F": "<33"}],
                ";p":  [{"F": ";p"}],
                ";D":  [{"F": ";D"}],
                ";-p": [{"F": ";-p"}],
                ";(":  [{"F": ";("}],
                ":p":  [{"F": ":p"}],
                ":]":  [{"F": ":]"}],
                ":O":  [{"F": ":O"}],
                ":-/": [{"F": ":-/"}],
                ":-)": [{"F": ":-)"}],
                ":(((":    [{"F": ":((("}],
                ":((": [{"F": ":(("}],
                ":')": [{"F": ":')"}],
                "(^_^)":   [{"F": "(^_^)"}],
                "(=":  [{"F": "(="}],
                "o.O": [{"F": "o.O"}],
                "\")": [{"F": "\")"}],
                "a.": [{"F": "a."}],
                "b.": [{"F": "b."}],
                "c.": [{"F": "c."}],
                "d.": [{"F": "d."}],
                "e.": [{"F": "e."}],
                "f.": [{"F": "f."}],
                "g.": [{"F": "g."}],
                "h.": [{"F": "h."}],
                "i.": [{"F": "i."}],
                "j.": [{"F": "j."}],
                "k.": [{"F": "k."}],
                "l.": [{"F": "l."}],
                "m.": [{"F": "m."}],
                "n.": [{"F": "n."}],
                "o.": [{"F": "o."}],
                "p.": [{"F": "p."}],
                "q.": [{"F": "q."}],
                "r.": [{"F": "r."}],
                "s.": [{"F": "s."}],
                "t.": [{"F": "t."}],
                "u.": [{"F": "u."}],
                "v.": [{"F": "v."}],
                "w.": [{"F": "w."}],
                "x.": [{"F": "x."}],
                "y.": [{"F": "y."}],
                "z.": [{"F": "z."}],

                "i.e.": [{"F": "i.e."}],
                "I.e.": [{"F": "I.e."}],
                "I.E.": [{"F": "I.E."}],
                "e.g.": [{"F": "e.g."}],
                "E.g.": [{"F": "E.g."}],
                "E.G.": [{"F": "E.G."}],
                "\n": [{"F": "\n", "pos": "SP"}],
                "\t": [{"F": "\t", "pos": "SP"}],
                " ": [{"F": " ", "pos": "SP"}],
                u"\u00a0": [{"F": u"\u00a0", "pos": "SP", "L": "  "}]

}

def get_double_contractions(ending):
    endings = []

    ends_with_contraction = any([ending.endswith(contraction) for contraction in contractions])

    while ends_with_contraction:
        for contraction in contractions:
            if ending.endswith(contraction):
                endings.append(contraction)
                ending = ending.rstrip(contraction)
        ends_with_contraction = any([ending.endswith(contraction) for contraction in contractions])

    endings.reverse() # reverse because the last ending is put in the list first
    return endings

def get_token_properties(token, capitalize=False, remove_contractions=False):
    props = dict(token_properties.get(token)) # ensure we copy the dict so we can add the "F" prop
    if capitalize:
        token = token.capitalize()
    if remove_contractions:
        token = token.replace("'", "")

    props["F"] = token
    return props

def create_entry(token, endings, capitalize=False, remove_contractions=False):
    
    properties = []
    properties.append(get_token_properties(token, capitalize=capitalize, remove_contractions=remove_contractions))
    for e in endings:
        properties.append(get_token_properties(e, remove_contractions=remove_contractions))
    return properties

def generate_specials():

    specials = {}

    for token in starting_tokens:
        possible_endings = starting_tokens[token]
        for ending in possible_endings:

            endings = []
            if ending.count("'") > 1:
                endings.extend(get_double_contractions(ending))
            else:
                endings.append(ending)

            exceptions = possible_endings[ending]

            if "lower" not in exceptions:
                special = token + ending
                specials[special] = create_entry(token, endings)

            if "upper" not in exceptions:
                special = token.capitalize() + ending
                specials[special] = create_entry(token, endings, capitalize=True)

            if "contrLower" not in exceptions:
                special = token + ending.replace("'", "")
                specials[special] = create_entry(token, endings, remove_contractions=True)

            if "contrUpper" not in exceptions:
                special = token.capitalize() + ending.replace("'", "")
                specials[special] = create_entry(token, endings, capitalize=True, remove_contractions=True)

    # add in hardcoded specials
    specials = dict(specials, **hardcoded_specials)

    return specials

if __name__ == "__main__":
    specials = generate_specials()
    with open("specials.json", "w") as file_:
        file_.write(json.dumps(specials, indent=2))


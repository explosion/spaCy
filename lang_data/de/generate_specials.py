# coding=utf8
import json
import io
import itertools

contractions = {}

# contains the lemmas, parts of speech, number, and tenspect of
# potential tokens generated after splitting contractions off
token_properties = {}

# contains starting tokens with their potential contractions
# each potential contraction has a list of exceptions
    # lower - don't generate the lowercase version
    # upper - don't generate the uppercase version
    # contrLower - don't generate the lowercase version with apostrophe (') removed
    # contrUpper - dont' generate the uppercase version with apostrophe (') removed
# for example, we don't want to create the word "hell" or "Hell" from "he" + "'ll" so 
# we add "contrLower" and "contrUpper" to the exceptions list
starting_tokens = {}

# other specials that don't really have contractions
# so they are hardcoded
hardcoded_specials = {
                "''": [{"F": "''"}],
                "\")": [{"F": "\")"}],
                "\n": [{"F": "\n", "pos": "SP"}],
                "\t": [{"F": "\t", "pos": "SP"}],
                " ": [{"F": " ", "pos": "SP"}],

                # example: Wie geht's?
                "'s":  [{"F": "'s", "L": "es"}],
                "'S":  [{"F": "'S", "L": "es"}],

                # example: Haste mal 'nen Euro?
                "'n":  [{"F": "'n", "L": "ein"}],
                "'ne":  [{"F": "'ne", "L": "eine"}],
                "'nen":  [{"F": "'nen", "L": "einen"}],

                # example: Kommen S’ nur herein!
                "s'":  [{"F": "s'", "L": "sie"}],
                "S'":  [{"F": "S'", "L": "sie"}],

                # example: Da haben wir's!
                "ich's":  [{"F": "ich"}, {"F": "'s", "L": "es"}],
                "du's":  [{"F": "du"}, {"F": "'s", "L": "es"}],
                "er's":  [{"F": "er"}, {"F": "'s", "L": "es"}],
                "sie's":  [{"F": "sie"}, {"F": "'s", "L": "es"}],
                "wir's":  [{"F": "wir"}, {"F": "'s", "L": "es"}],
                "ihr's":  [{"F": "ihr"}, {"F": "'s", "L": "es"}],

                # example: Die katze auf'm dach.
                "auf'm":  [{"F": "auf"}, {"F": "'m", "L": "dem"}],
                "unter'm":  [{"F": "unter"}, {"F": "'m", "L": "dem"}],
                "über'm":  [{"F": "über"}, {"F": "'m", "L": "dem"}],
                "vor'm":  [{"F": "vor"}, {"F": "'m", "L": "dem"}],
                "hinter'm":  [{"F": "hinter"}, {"F": "'m", "L": "dem"}],

                # persons
                "Fr.": [{"F": "Fr."}],
                "Hr.": [{"F": "Hr."}],
                "Frl.": [{"F": "Frl."}],
                "Prof.": [{"F": "Prof."}],
                "Dr.": [{"F": "Dr."}],
                "St.": [{"F": "St."}],
                "Hrgs.": [{"F": "Hrgs."}],
                "Hg.": [{"F": "Hg."}],
                "a.Z.": [{"F": "a.Z."}],
                "a.D.": [{"F": "a.D."}],
                "A.D.": [{"F": "A.D."}],
                "h.c.": [{"F": "h.c."}],
                "jun.": [{"F": "jun."}],
                "sen.": [{"F": "sen."}],
                "rer.": [{"F": "rer."}],
                "Dipl.": [{"F": "Dipl."}],
                "Ing.": [{"F": "Ing."}],
                "Dipl.-Ing.": [{"F": "Dipl.-Ing."}],

                # companies
                "Co.": [{"F": "Co."}],
                "co.": [{"F": "co."}],
                "Cie.": [{"F": "Cie."}],
                "A.G.": [{"F": "A.G."}],
                "G.m.b.H.": [{"F": "G.m.b.H."}],
                "i.G.": [{"F": "i.G."}],
                "e.V.": [{"F": "e.V."}],

                # popular german abbreviations
                "ggü.": [{"F": "ggü."}],
                "ggf.": [{"F": "ggf."}],
                "ggfs.": [{"F": "ggfs."}],
                "Gebr.": [{"F": "Gebr."}],
                "geb.": [{"F": "geb."}],
                "gegr.": [{"F": "gegr."}],
                "erm.": [{"F": "erm."}],
                "engl.": [{"F": "engl."}],
                "ehem.": [{"F": "ehem."}],
                "Biol.": [{"F": "Biol."}],
                "biol.": [{"F": "biol."}],
                "Abk.": [{"F": "Abk."}],
                "Abb.": [{"F": "Abb."}],
                "abzgl.": [{"F": "abzgl."}],
                "Hbf.": [{"F": "Hbf."}],
                "Bhf.": [{"F": "Bhf."}],
                "Bf.": [{"F": "Bf."}],
                "i.V.": [{"F": "i.V."}],
                "inkl.": [{"F": "inkl."}],
                "insb.": [{"F": "insb."}],
                "z.B.": [{"F": "z.B."}],
                "i.Tr.": [{"F": "i.Tr."}],
                "Jhd.": [{"F": "Jhd."}],
                "jur.": [{"F": "jur."}],
                "lt.": [{"F": "lt."}],
                "nat.": [{"F": "nat."}],
                "u.a.": [{"F": "u.a."}],
                "u.s.w.": [{"F": "u.s.w."}],
                "Nr.": [{"F": "Nr."}],
                "Univ.": [{"F": "Univ."}],
                "vgl.": [{"F": "vgl."}],
                "zzgl.": [{"F": "zzgl."}],
                "z.Z.": [{"F": "z.Z."}],
                "betr.": [{"F": "betr."}],
                "ehem.": [{"F": "ehem."}],

                # popular latin abbreviations
                "vs.": [{"F": "vs."}],
                "adv.": [{"F": "adv."}],
                "Chr.": [{"F": "Chr."}],
                "A.C.": [{"F": "A.C."}],
                "A.D.": [{"F": "A.D."}],
                "e.g.": [{"F": "e.g."}],
                "i.e.": [{"F": "i.e."}],
                "al.": [{"F": "al."}],
                "p.a.": [{"F": "p.a."}],
                "P.S.": [{"F": "P.S."}],
                "q.e.d.": [{"F": "q.e.d."}],
                "R.I.P.": [{"F": "R.I.P."}],
                "etc.": [{"F": "etc."}],
                "incl.": [{"F": "incl."}],

                # popular english abbreviations
                "D.C.": [{"F": "D.C."}],
                "N.Y.": [{"F": "N.Y."}],
                "N.Y.C.": [{"F": "N.Y.C."}],

                # dates
                "Jan.": [{"F": "Jan."}],
                "Feb.": [{"F": "Feb."}],
                "Mrz.": [{"F": "Mrz."}],
                "Mär.": [{"F": "Mär."}],
                "Apr.": [{"F": "Apr."}],
                "Jun.": [{"F": "Jun."}],
                "Jul.": [{"F": "Jul."}],
                "Aug.": [{"F": "Aug."}],
                "Sep.": [{"F": "Sep."}],
                "Sept.": [{"F": "Sept."}],
                "Okt.": [{"F": "Okt."}],
                "Nov.": [{"F": "Nov."}],
                "Dez.": [{"F": "Dez."}],
                "Mo.": [{"F": "Mo."}],
                "Di.": [{"F": "Di."}],
                "Mi.": [{"F": "Mi."}],
                "Do.": [{"F": "Do."}],
                "Fr.": [{"F": "Fr."}],
                "Sa.": [{"F": "Sa."}],
                "So.": [{"F": "So."}],

                # smileys
                ":)":    [{"F": ":)"}],
                "<3":    [{"F": "<3"}],
                ";)":    [{"F": ";)"}],
                "(:":    [{"F": "(:"}],
                ":(":    [{"F": ":("}],
                "-_-":   [{"F": "-_-"}],
                "=)":    [{"F": "=)"}],
                ":/":    [{"F": ":/"}],
                ":>":    [{"F": ":>"}],
                ";-)":   [{"F": ";-)"}],
                ":Y":    [{"F": ":Y"}],
                ":P":    [{"F": ":P"}],
                ":-P":   [{"F": ":-P"}],
                ":3":    [{"F": ":3"}],
                "=3":    [{"F": "=3"}],
                "xD":    [{"F": "xD"}],
                "^_^":   [{"F": "^_^"}],
                "=]":    [{"F": "=]"}],
                "=D":    [{"F": "=D"}],
                "<333":  [{"F": "<333"}],
                ":))":   [{"F": ":))"}],
                ":0":    [{"F": ":0"}],
                "-__-":  [{"F": "-__-"}],
                "xDD":   [{"F": "xDD"}],
                "o_o":   [{"F": "o_o"}],
                "o_O":   [{"F": "o_O"}],
                "V_V":   [{"F": "V_V"}],
                "=[[":   [{"F": "=[["}],
                "<33":   [{"F": "<33"}],
                ";p":    [{"F": ";p"}],
                ";D":    [{"F": ";D"}],
                ";-p":   [{"F": ";-p"}],
                ";(":    [{"F": ";("}],
                ":p":    [{"F": ":p"}],
                ":]":    [{"F": ":]"}],
                ":O":    [{"F": ":O"}],
                ":-/":   [{"F": ":-/"}],
                ":-)":   [{"F": ":-)"}],
                ":(((":  [{"F": ":((("}],
                ":((":   [{"F": ":(("}],
                ":')":   [{"F": ":')"}],
                "(^_^)": [{"F": "(^_^)"}],
                "(=":    [{"F": "(="}],
                "o.O":   [{"F": "o.O"}],

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


FIELDNAMES = ['F','L','pos']
def read_hardcoded(stream):
    hc_specials = {}
    for line in stream:
        line = line.strip()
        if line.startswith('#') or not line:
            continue
        key,_,rest = line.partition('\t')
        values = []
        for annotation in zip(*[ e.split('|') for e in rest.split('\t') ]):
            values.append({ k:v for k,v in itertools.izip_longest(FIELDNAMES,annotation) if v })
        hc_specials[key] = values
    return hc_specials


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
    # changed it so it generates them from a file
    with io.open('abbrev.de.tab','r',encoding='utf8') as abbrev_:
        hc_specials = read_hardcoded(abbrev_)
    specials = dict(specials, **hc_specials)

    return specials

if __name__ == "__main__":
    specials = generate_specials()
    with open("specials.json", "w") as f:
        json.dump(specials, f, sort_keys=True, indent=4, separators=(',', ': '))

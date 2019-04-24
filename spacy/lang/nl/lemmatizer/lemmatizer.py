# coding: utf8
from __future__ import unicode_literals

from ....symbols import POS, NOUN, VERB, ADJ, NUM, DET, PRON, ADP, AUX, ADV


class DutchLemmatizer(object):
    # Note: CGN does not distinguish AUX verbs, so we treat AUX as VERB.
    univ_pos_name_variants = {
        NOUN: "noun", "NOUN": "noun", "noun": "noun",
        VERB: "verb", "VERB": "verb", "verb": "verb",
        AUX: "verb", "AUX": "verb", "aux": "verb",
        ADJ: "adj", "ADJ": "adj", "adj": "adj",
        ADV: "adv", "ADV": "adv", "adv": "adv",
        PRON: "pron", "PRON": "pron", "pron": "pron",
        DET: "det", "DET": "det", "det": "det",
        ADP: "adp", "ADP": "adp", "adp": "adp",
        NUM: "num", "NUM": "num", "num": "num"
    }

    @classmethod
    def load(cls, path, index=None, exc=None, rules=None, lookup=None):
        return cls(index, exc, rules, lookup)

    def __init__(self, index=None, exceptions=None, rules=None, lookup=None):
        self.index = index
        self.exc = exceptions
        self.rules = rules or {}
        self.lookup_table = lookup if lookup is not None else {}

    def __call__(self, string, univ_pos, morphology=None):
        # Difference 1: self.rules is assumed to be non-None, so no
        # 'is None' check required.
        # String lowercased from the get-go. All lemmatization results in
        # lowercased strings. For most applications, this shouldn't pose
        # any problems, and it keeps the exceptions indexes small. If this
        # creates problems for proper nouns, we can introduce a check for
        # univ_pos == "PROPN".
        string = string.lower()
        try:
            univ_pos = self.univ_pos_name_variants[univ_pos]
        except KeyError:
            # Because PROPN not in self.univ_pos_name_variants, proper names
            # are not lemmatized. They are lowercased, however.
            return [string]
            # if string in self.lemma_index.get(univ_pos)
        lemma_index = self.index.get(univ_pos, {})
        # string is already lemma
        if string in lemma_index:
            return [string]
        exceptions = self.exc.get(univ_pos, {})
        # string is irregular token contained in exceptions index.
        try:
            lemma = exceptions[string]
            return [lemma[0]]
        except KeyError:
            pass
        # string corresponds to  key in lookup table
        lookup_table = self.lookup_table
        looked_up_lemma = lookup_table.get(string)
        if looked_up_lemma and looked_up_lemma in lemma_index:
            return [looked_up_lemma]

        forms, is_known = lemmatize(
            string,
            lemma_index,
            exceptions,
            self.rules.get(univ_pos, []))

        # Back-off through remaining return value candidates.
        if forms:
            if is_known:
                return forms
            else:
                for form in forms:
                    if form in exceptions:
                        return [form]
            if looked_up_lemma:
                return [looked_up_lemma]
            else:
                return forms
        elif looked_up_lemma:
            return [looked_up_lemma]
        else:
            return [string]

    # Overrides parent method so that a lowercased version of the string is
    # used to search the lookup table. This is necessary because our lookup
    # table consists entirely of lowercase keys.
    def lookup(self, string):
        string = string.lower()
        return self.lookup_table.get(string, string)

    def noun(self, string, morphology=None):
        return self(string, 'noun', morphology)

    def verb(self, string, morphology=None):
        return self(string, 'verb', morphology)

    def adj(self, string, morphology=None):
        return self(string, 'adj', morphology)

    def det(self, string, morphology=None):
        return self(string, 'det', morphology)

    def pron(self, string, morphology=None):
        return self(string, 'pron', morphology)

    def adp(self, string, morphology=None):
        return self(string, 'adp', morphology)

    def punct(self, string, morphology=None):
        return self(string, 'punct', morphology)


# Reimplemented to focus more on application of suffix rules and to return
# as early as possible.
def lemmatize(string, index, exceptions, rules):
    # returns (forms, is_known: bool)
    oov_forms = []
    for old, new in rules:
        if string.endswith(old):
            form = string[:len(string) - len(old)] + new
            if not form:
                pass
            elif form in index:
                return [form], True  # True = Is known (is lemma)
            else:
                oov_forms.append(form)
    return list(set(oov_forms)), False

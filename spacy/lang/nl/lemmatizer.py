# coding: utf8
from __future__ import unicode_literals

from ...lemmatizer import Lemmatizer
from ...symbols import NOUN, VERB, ADJ, NUM, DET, PRON, ADP, AUX, ADV


class DutchLemmatizer(Lemmatizer):
    # Note: CGN does not distinguish AUX verbs, so we treat AUX as VERB.
    univ_pos_name_variants = {
        NOUN: "noun",
        "NOUN": "noun",
        "noun": "noun",
        VERB: "verb",
        "VERB": "verb",
        "verb": "verb",
        AUX: "verb",
        "AUX": "verb",
        "aux": "verb",
        ADJ: "adj",
        "ADJ": "adj",
        "adj": "adj",
        ADV: "adv",
        "ADV": "adv",
        "adv": "adv",
        PRON: "pron",
        "PRON": "pron",
        "pron": "pron",
        DET: "det",
        "DET": "det",
        "det": "det",
        ADP: "adp",
        "ADP": "adp",
        "adp": "adp",
        NUM: "num",
        "NUM": "num",
        "num": "num",
    }

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
        index_table = self.lookups.get_table("lemma_index", {})
        lemma_index = index_table.get(univ_pos, {})
        # string is already lemma
        if string in lemma_index:
            return [string]
        exc_table = self.lookups.get_table("lemma_exc", {})
        exceptions = exc_table.get(univ_pos, {})
        # string is irregular token contained in exceptions index.
        try:
            lemma = exceptions[string]
            return [lemma[0]]
        except KeyError:
            pass
        # string corresponds to key in lookup table
        lookup_table = self.lookups.get_table("lemma_lookup", {})
        looked_up_lemma = lookup_table.get(string)
        if looked_up_lemma and looked_up_lemma in lemma_index:
            return [looked_up_lemma]
        rules_table = self.lookups.get_table("lemma_rules", {})
        forms, is_known = self.lemmatize(
            string, lemma_index, exceptions, rules_table.get(univ_pos, [])
        )
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
    def lookup(self, string, orth=None):
        lookup_table = self.lookups.get_table("lemma_lookup", {})
        string = string.lower()
        if orth is not None:
            return lookup_table.get(orth, string)
        else:
            return lookup_table.get(string, string)

    # Reimplemented to focus more on application of suffix rules and to return
    # as early as possible.
    def lemmatize(self, string, index, exceptions, rules):
        # returns (forms, is_known: bool)
        oov_forms = []
        for old, new in rules:
            if string.endswith(old):
                form = string[: len(string) - len(old)] + new
                if not form:
                    pass
                elif form in index:
                    return [form], True  # True = Is known (is lemma)
                else:
                    oov_forms.append(form)
        return list(set(oov_forms)), False

# coding: utf-8
from __future__ import unicode_literals

from ...lemmatizer import Lemmatizer
from ...parts_of_speech import NAMES
from ...errors import Errors


class PolishLemmatizer(Lemmatizer):
    # This lemmatizer implements lookup lemmatization based on
    # the Morfeusz dictionary (morfeusz.sgjp.pl/en) by Institute of Computer Science PAS
    # It utilizes some prefix based improvements for
    # verb and adjectives lemmatization, as well as case-sensitive
    # lemmatization for nouns
    def __init__(self, lookups, *args, **kwargs):
        # this lemmatizer is lookup based, so it does not require an index, exceptionlist, or rules
        super(PolishLemmatizer, self).__init__(lookups)
        self.lemma_lookups = {}
        for tag in [
            "ADJ",
            "ADP",
            "ADV",
            "AUX",
            "NOUN",
            "NUM",
            "PART",
            "PRON",
            "VERB",
            "X",
        ]:
            self.lemma_lookups[tag] = self.lookups.get_table(
                "lemma_lookup_" + tag.lower(), {}
            )
        self.lemma_lookups["DET"] = self.lemma_lookups["X"]
        self.lemma_lookups["PROPN"] = self.lemma_lookups["NOUN"]

    def __call__(self, string, univ_pos, morphology=None):
        if isinstance(univ_pos, int):
            univ_pos = NAMES.get(univ_pos, "X")
        univ_pos = univ_pos.upper()

        if univ_pos == "NOUN":
            return self.lemmatize_noun(string, morphology)

        if univ_pos != "PROPN":
            string = string.lower()

        if univ_pos == "ADJ":
            return self.lemmatize_adj(string, morphology)
        elif univ_pos == "VERB":
            return self.lemmatize_verb(string, morphology)

        lemma_dict = self.lemma_lookups.get(univ_pos, {})
        return [lemma_dict.get(string, string.lower())]

    def lemmatize_adj(self, string, morphology):
        # this method utilizes different procedures for adjectives
        # with 'nie' and 'naj' prefixes
        lemma_dict = self.lemma_lookups["ADJ"]

        if string[:3] == "nie":
            search_string = string[3:]
            if search_string[:3] == "naj":
                naj_search_string = search_string[3:]
                if naj_search_string in lemma_dict:
                    return [lemma_dict[naj_search_string]]
            if search_string in lemma_dict:
                return [lemma_dict[search_string]]

        if string[:3] == "naj":
            naj_search_string = string[3:]
            if naj_search_string in lemma_dict:
                return [lemma_dict[naj_search_string]]

        return [lemma_dict.get(string, string)]

    def lemmatize_verb(self, string, morphology):
        # this method utilizes a different procedure for verbs
        # with 'nie' prefix
        lemma_dict = self.lemma_lookups["VERB"]

        if string[:3] == "nie":
            search_string = string[3:]
            if search_string in lemma_dict:
                return [lemma_dict[search_string]]

        return [lemma_dict.get(string, string)]

    def lemmatize_noun(self, string, morphology):
        # this method is case-sensitive, in order to work
        # for incorrectly tagged proper names
        lemma_dict = self.lemma_lookups["NOUN"]

        if string != string.lower():
            if string.lower() in lemma_dict:
                return [lemma_dict[string.lower()]]
            elif string in lemma_dict:
                return [lemma_dict[string]]
            return [string.lower()]

        return [lemma_dict.get(string, string)]

    def lookup(self, string, orth=None):
        return string.lower()

    def lemmatize(self, string, index, exceptions, rules):
        raise NotImplementedError

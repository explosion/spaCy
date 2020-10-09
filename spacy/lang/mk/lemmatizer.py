# coding: utf8
from __future__ import unicode_literals

from collections import OrderedDict

from ...lemmatizer import Lemmatizer
from ...parts_of_speech import NAMES as UPOS_NAMES


class MacedonianLemmatizer(Lemmatizer):
    def __call__(self, string, univ_pos, morphology=None):
        lookup_table = self.lookups.get_table("lemma_lookup", {})
        if "lemma_rules" not in self.lookups:
            return [lookup_table.get(string, string)]
        if isinstance(univ_pos, int):
            univ_pos = UPOS_NAMES.get(univ_pos, "X")
        univ_pos = univ_pos.lower()

        if univ_pos in ("", "eol", "space"):
            return [string.lower()]

        if string[-3:] == 'јќи':
            string = string[:-3]
            univ_pos = "verb"

        if callable(self.is_base_form) and self.is_base_form(univ_pos, morphology):
            return [string.lower()]
        index_table = self.lookups.get_table("lemma_index", {})
        exc_table = self.lookups.get_table("lemma_exc", {})
        rules_table = self.lookups.get_table("lemma_rules", {})
        if not any((index_table.get(univ_pos), exc_table.get(univ_pos), rules_table.get(univ_pos))):
            if univ_pos == "propn":
                return [string]
            else:
                return [string.lower()]
        lemmas = self.lemmatize(
            string,
            index_table.get(univ_pos, {}),
            exc_table.get(univ_pos, {}),
            rules_table.get(univ_pos, []),
        )
        return lemmas

    def lemmatize(self, string, index, exceptions, rules):
        orig = string
        string = string.lower()
        forms = []

        for old, new in rules:
            if string.endswith(old):
                form = string[: len(string) - len(old)] + new
                if not form:
                    continue
                if form in index or not form.isalpha():
                    forms.append(form)

        forms = list(OrderedDict.fromkeys(forms))
        for form in exceptions.get(string, []):
            if form not in forms:
                forms.insert(0, form)
        if not forms:
            forms.append(orig)

        return forms

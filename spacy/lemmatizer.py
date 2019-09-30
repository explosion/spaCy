# coding: utf8
from __future__ import unicode_literals
from collections import OrderedDict

from .symbols import POS, NOUN, VERB, ADJ, PUNCT, PROPN
from .symbols import VerbForm_inf, VerbForm_none, Number_sing, Degree_pos


class Lemmatizer(object):
    """
    The Lemmatizer supports simple part-of-speech-sensitive suffix rules and
    lookup tables.

    DOCS: https://spacy.io/api/lemmatizer
    """

    @classmethod
    def load(cls, path, index=None, exc=None, rules=None, lookup=None):
        return cls(index, exc, rules, lookup)

    def __init__(self, index=None, exceptions=None, rules=None, lookup=None):
        self.index = index
        self.exc = exceptions
        self.rules = rules
        self.lookup_table = lookup if lookup is not None else {}

    def __call__(self, string, univ_pos, morphology=None):
        if not self.rules:
            return [self.lookup_table.get(string, string)]
        if univ_pos in (NOUN, "NOUN", "noun"):
            univ_pos = "noun"
        elif univ_pos in (VERB, "VERB", "verb"):
            univ_pos = "verb"
        elif univ_pos in (ADJ, "ADJ", "adj"):
            univ_pos = "adj"
        elif univ_pos in (PUNCT, "PUNCT", "punct"):
            univ_pos = "punct"
        elif univ_pos in (PROPN, "PROPN"):
            return [string]
        else:
            return [string.lower()]
        # See Issue #435 for example of where this logic is requied.
        if self.is_base_form(univ_pos, morphology):
            return [string.lower()]
        lemmas = lemmatize(
            string,
            self.index.get(univ_pos, {}),
            self.exc.get(univ_pos, {}),
            self.rules.get(univ_pos, []),
        )
        return lemmas

    def is_base_form(self, univ_pos, morphology=None):
        """
        Check whether we're dealing with an uninflected paradigm, so we can
        avoid lemmatization entirely.
        """
        morphology = {} if morphology is None else morphology
        others = [
            key
            for key in morphology
            if key not in (POS, "Number", "POS", "VerbForm", "Tense")
        ]
        if univ_pos == "noun" and morphology.get("Number") == "sing":
            return True
        elif univ_pos == "verb" and morphology.get("VerbForm") == "inf":
            return True
        # This maps 'VBP' to base form -- probably just need 'IS_BASE'
        # morphology
        elif univ_pos == "verb" and (
            morphology.get("VerbForm") == "fin"
            and morphology.get("Tense") == "pres"
            and morphology.get("Number") is None
            and not others
        ):
            return True
        elif univ_pos == "adj" and morphology.get("Degree") == "pos":
            return True
        elif VerbForm_inf in morphology:
            return True
        elif VerbForm_none in morphology:
            return True
        elif Number_sing in morphology:
            return True
        elif Degree_pos in morphology:
            return True
        else:
            return False

    def noun(self, string, morphology=None):
        return self(string, "noun", morphology)

    def verb(self, string, morphology=None):
        return self(string, "verb", morphology)

    def adj(self, string, morphology=None):
        return self(string, "adj", morphology)

    def punct(self, string, morphology=None):
        return self(string, "punct", morphology)

    def lookup(self, string):
        if string in self.lookup_table:
            return self.lookup_table[string]
        return string


def lemmatize(string, index, exceptions, rules):
    orig = string
    string = string.lower()
    forms = []
    oov_forms = []
    for old, new in rules:
        if string.endswith(old):
            form = string[: len(string) - len(old)] + new
            if not form:
                pass
            elif form in index or not form.isalpha():
                forms.append(form)
            else:
                oov_forms.append(form)
    # Remove duplicates but preserve the ordering of applied "rules"
    forms = list(OrderedDict.fromkeys(forms))
    # Put exceptions at the front of the list, so they get priority.
    # This is a dodgy heuristic -- but it's the best we can do until we get
    # frequencies on this. We can at least prune out problematic exceptions,
    # if they shadow more frequent analyses.
    for form in exceptions.get(string, []):
        if form not in forms:
            forms.insert(0, form)
    if not forms:
        forms.extend(oov_forms)
    if not forms:
        forms.append(orig)
    return forms

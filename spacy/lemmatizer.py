# coding: utf8
from __future__ import unicode_literals

from collections import OrderedDict

from .symbols import NOUN, VERB, ADJ, PUNCT, PROPN
from .errors import Errors
from .lookups import Lookups


class Lemmatizer(object):
    """
    The Lemmatizer supports simple part-of-speech-sensitive suffix rules and
    lookup tables.

    DOCS: https://spacy.io/api/lemmatizer
    """

    @classmethod
    def load(cls, *args, **kwargs):
        raise NotImplementedError(Errors.E172)

    def __init__(self, lookups, *args, **kwargs):
        """Initialize a Lemmatizer.

        lookups (Lookups): The lookups object containing the (optional) tables
            "lemma_rules", "lemma_index", "lemma_exc" and "lemma_lookup".
        RETURNS (Lemmatizer): The newly constructed object.
        """
        if args or kwargs or not isinstance(lookups, Lookups):
            raise ValueError(Errors.E173)
        self.lookups = lookups

    def __call__(self, string, univ_pos, morphology=None):
        """Lemmatize a string.

        string (unicode): The string to lemmatize, e.g. the token text.
        univ_pos (unicode / int): The token's universal part-of-speech tag.
        morphology (dict): The token's morphological features following the
            Universal Dependencies scheme.
        RETURNS (list): The available lemmas for the string.
        """
        lookup_table = self.lookups.get_table("lemma_lookup", {})
        if "lemma_rules" not in self.lookups:
            return [lookup_table.get(string, string)]
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
        index_table = self.lookups.get_table("lemma_index", {})
        exc_table = self.lookups.get_table("lemma_exc", {})
        rules_table = self.lookups.get_table("lemma_rules", {})
        lemmas = self.lemmatize(
            string,
            index_table.get(univ_pos, {}),
            exc_table.get(univ_pos, {}),
            rules_table.get(univ_pos, []),
        )
        return lemmas

    def is_base_form(self, univ_pos, morphology=None):
        """
        Check whether we're dealing with an uninflected paradigm, so we can
        avoid lemmatization entirely.

        univ_pos (unicode / int): The token's universal part-of-speech tag.
        morphology (dict): The token's morphological features following the
            Universal Dependencies scheme.
        """
        if morphology is None:
            morphology = {}
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
        ):
            return True
        elif univ_pos == "adj" and morphology.get("Degree") == "pos":
            return True
        elif morphology.get("VerbForm") == "inf":
            return True
        elif morphology.get("VerbForm") == "none":
            return True
        elif morphology.get("VerbForm") == "inf":
            return True
        elif morphology.get("Degree") == "pos":
            return True
        else:
            return False

    def noun(self, string, morphology=None):
        return self(string, "noun", morphology)

    def verb(self, string, morphology=None):
        return self(string, "verb", morphology)

    def adj(self, string, morphology=None):
        return self(string, "adj", morphology)

    def det(self, string, morphology=None):
        return self(string, "det", morphology)

    def pron(self, string, morphology=None):
        return self(string, "pron", morphology)

    def adp(self, string, morphology=None):
        return self(string, "adp", morphology)

    def num(self, string, morphology=None):
        return self(string, "num", morphology)

    def punct(self, string, morphology=None):
        return self(string, "punct", morphology)

    def lookup(self, string, orth=None):
        """Look up a lemma in the table, if available. If no lemma is found,
        the original string is returned.

        string (unicode): The original string.
        orth (int): Optional hash of the string to look up. If not set, the
            string will be used and hashed.
        RETURNS (unicode): The lemma if the string was found, otherwise the
            original string.
        """
        lookup_table = self.lookups.get_table("lemma_lookup", {})
        key = orth if orth is not None else string
        if key in lookup_table:
            return lookup_table[key]
        return string

    def lemmatize(self, string, index, exceptions, rules):
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

# coding: utf8
from __future__ import unicode_literals

from ....symbols import NOUN, VERB, ADJ, PUNCT


class GreekLemmatizer(object):
    """
    Greek language lemmatizer applies the default rule based lemmatization
    procedure with some modifications for better Greek language support.

    The first modification is that it checks if the word for lemmatization is
    already a lemma and if yes, it just returns it.
    The second modification is about removing the base forms function which is
    not applicable for Greek language.
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
        else:
            return list(set([string.lower()]))
        lemmas = lemmatize(
            string,
            self.index.get(univ_pos, {}),
            self.exc.get(univ_pos, {}),
            self.rules.get(univ_pos, []),
        )
        return lemmas


def lemmatize(string, index, exceptions, rules):
    string = string.lower()
    forms = []
    if string in index:
        forms.append(string)
        return forms
    forms.extend(exceptions.get(string, []))
    oov_forms = []
    if not forms:
        for old, new in rules:
            if string.endswith(old):
                form = string[: len(string) - len(old)] + new
                if not form:
                    pass
                elif form in index or not form.isalpha():
                    forms.append(form)
                else:
                    oov_forms.append(form)
    if not forms:
        forms.extend(oov_forms)
    if not forms:
        forms.append(string)
    return list(set(forms))

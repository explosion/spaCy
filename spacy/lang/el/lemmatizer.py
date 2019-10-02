# coding: utf8
from __future__ import unicode_literals

from ...lemmatizer import Lemmatizer


class GreekLemmatizer(Lemmatizer):
    """
    Greek language lemmatizer applies the default rule based lemmatization
    procedure with some modifications for better Greek language support.

    The first modification is that it checks if the word for lemmatization is
    already a lemma and if yes, it just returns it.
    The second modification is about removing the base forms function which is
    not applicable for Greek language.
    """

    def lemmatize(self, string, index, exceptions, rules):
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

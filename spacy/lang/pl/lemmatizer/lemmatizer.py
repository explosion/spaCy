#coding: utf-8
import re

from ....symbols import NOUN, VERB, ADJ, PUNCT


class PolishLemmatizer(object):
    @classmethod
    def load(cls, path, index=None, exc=None, rules=None, lookup=None):
        return cls(index, exc, rules, lookup)

    def __init__(self, index=None, exceptions=None, rules=None, lookup=None):
        self.index = index
        self.exc = exceptions
        self.rules = rules
        self.lookup_table = lookup if lookup is not None else {}

    def __call__(self, string, univ_pos, morphology=None):
        if univ_pos in (NOUN, 'NOUN', 'noun'):
            univ_pos = 'noun'
        elif univ_pos in (VERB, 'VERB', 'verb'):
            univ_pos = 'verb'
        elif univ_pos in (ADJ, 'ADJ', 'adj'):
            univ_pos = 'adj'
        else:
            univ_pos = 'any'

        if univ_pos == 'any':
            index_all = {word for word_list in self.index.values() for word in word_list}
            exc_all = [exc for exc_list in self.exc.values() for exc in exc_list]
            rules_all = [rule for rule_list in self.rules.values() for rule in rule_list]
            lemmas = lemmatize(string, index_all, exc_all, rules_all)
        else:
            lemmas = lemmatize(string,
                               self.index.get(univ_pos, {}) | self.index.get('other', {}),
                               self.exc.get(univ_pos, {}).update(self.exc.get('other', {})),
                               self.rules.get(univ_pos, []) + self.rules.get('other', {})
                               )
        return lemmas

    def lookup(self, string):
        return string.lower()


def lemmatize(string, index, exceptions, rules):
    string = string.lower()
    forms = []
    if string in index:
        forms.append(string)

    oov_forms = []

    for old, new in rules:
        if re.search(r'{}$'.format(old), string):
            new_word_suf = old.replace('[', '([').replace(']', '])')
            new_lemma_suf = re.sub(r'\[.*\]', r'\\1', new)
            form = re.sub(r'{}$'.format(new_word_suf), r'{}'.format(new_lemma_suf), string)
            if form in index or not form.isalpha():
                forms.append(form)
            else:
                oov_forms.append(form)
    if not forms:
        forms.extend(oov_forms)
    if not forms:
        forms.append(string)
    return list(set(forms))

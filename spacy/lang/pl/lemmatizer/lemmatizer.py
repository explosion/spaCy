#coding: utf-8
import re

from ....symbols import NOUN, VERB, ADJ, PUNCT, ADV, PART
from .trie import Trie, trie_from_rules


class PolishLemmatizer(object):
    @classmethod
    def load(cls, path, index=None, exc=None, rules=None, lookup=None):
        return cls(index, exc, rules, lookup)

    def __init__(self, index=None, exceptions=None, rules=None, lookup=None):
        self.index = index
        self.exc = exceptions
        self.rules = rules
        self.lookup_table = lookup if lookup is not None else {}
        self.tries = {}
        for univ_pos in ['noun', 'verb', 'adj', 'adv', 'part']:
            self.tries[univ_pos] = trie_from_rules(self.rules.get(univ_pos, []) + self.rules.get('other', {}))

    def __call__(self, string, univ_pos, morphology=None):
        if univ_pos in (NOUN, 'NOUN', 'noun'):
            univ_pos = 'noun'
        elif univ_pos in (VERB, 'VERB', 'verb'):
            univ_pos = 'verb'
        elif univ_pos in (ADJ, 'ADJ', 'adj'):
            univ_pos = 'adj'
        elif univ_pos in (ADV, 'ADV', 'adv'):
            univ_pos = 'adv'
        elif univ_pos in (PART, 'PART', 'part'):
            univ_pos = 'part'
        else:
            return [self.lookup(string)]

        # TODO check if is base form
        
        exceptions = self.exc.get(univ_pos, {}).copy()
        exceptions.update(self.exc.get('other', {}))
        lemmas = lemmatize(string,
                                self.index.get(univ_pos, {}) | self.index.get('other', {}),
                                exceptions,
                                self.tries[univ_pos])
        # lemmas = lemmatize(
        #     string,
        #     self.index.get(univ_pos, {}) | self.index.get('other', {}),
        #     exceptions,
        #     self.rules.get(univ_pos, []) + self.rules.get('other', {})
        # )
        return lemmas

    def lookup(self, string):
        return string.lower()

def lemmatize(string, index, exceptions, trie):
    string = string.lower()
    forms = []
    if string in index:
        forms.append(string)

    oov_forms = []
    matches = trie.get_rules(string)
    for matched_rules in matches:
        for rule in matched_rules:
            form = re.sub(rule[0], rule[1], string)
            if form in index or not form.isalpha():
                forms.append(form)
            else:
                oov_forms.append(form)

    if not forms:
        forms.extend(oov_forms)
    if not forms:
        forms.append(string)
    return list(set(forms))


# def lemmatize(string, index, exceptions, rules):
#     string = string.lower()
#     forms = []
#     if string in index:
#         forms.append(string)
#
#     oov_forms = []
#     for word_suf, lemma_suf in rules:
#         if re.search(word_suf, string):
#             form = re.sub(word_suf, lemma_suf, string)
#             if form in index or not form.isalpha():
#                 forms.append(form)
#             else:
#                 oov_forms.append(form)
#     if not forms:
#         forms.extend(oov_forms)
#     if not forms:
#         forms.append(string)
#     return list(set(forms))

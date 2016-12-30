from __future__ import unicode_literals, print_function
import codecs
import pathlib

import ujson as json

from .symbols import POS, NOUN, VERB, ADJ, PUNCT


class Lemmatizer(object):
    @classmethod
    def load(cls, path, rules=None):
        index = {}
        exc = {}
        for pos in ['adj', 'noun', 'verb']:
            pos_index_path = path / 'wordnet' / 'index.{pos}'.format(pos=pos)
            if pos_index_path.exists():
                with pos_index_path.open() as file_:
                    index[pos] = read_index(file_)
            else:
                index[pos] = set()
            pos_exc_path = path / 'wordnet' / '{pos}.exc'.format(pos=pos)
            if pos_exc_path.exists():
                with pos_exc_path.open() as file_:
                    exc[pos] = read_exc(file_)
            else:
                exc[pos] = {}
        if rules is None and (path / 'vocab' / 'lemma_rules.json').exists():
            with (path / 'vocab' / 'lemma_rules.json').open('r', encoding='utf8') as file_:
                rules = json.load(file_)
        elif rules is None:
            rules = {}
        return cls(index, exc, rules)

    def __init__(self, index, exceptions, rules):
        self.index = index
        self.exc = exceptions
        self.rules = rules

    def __call__(self, string, univ_pos, morphology=None):
        if univ_pos == NOUN:
            univ_pos = 'noun'
        elif univ_pos == VERB:
            univ_pos = 'verb'
        elif univ_pos == ADJ:
            univ_pos = 'adj'
        elif univ_pos == PUNCT:
            univ_pos = 'punct'
        # See Issue #435 for example of where this logic is requied.
        if self.is_base_form(univ_pos, morphology):
            return set([string.lower()])
        lemmas = lemmatize(string, self.index.get(univ_pos, {}),
                           self.exc.get(univ_pos, {}),
                           self.rules.get(univ_pos, []))
        return lemmas

    def is_base_form(self, univ_pos, morphology=None):
        '''Check whether we're dealing with an uninflected paradigm, so we can
        avoid lemmatization entirely.'''
        morphology = {} if morphology is None else morphology
        others = [key for key in morphology if key not in (POS, 'number', 'pos', 'verbform')]
        if univ_pos == 'noun' and morphology.get('number') == 'sing' and not others:
            return True
        elif univ_pos == 'verb' and morphology.get('verbform') == 'inf' and not others:
            return True
        else:
            return False

    def noun(self, string, morphology=None):
        return self(string, 'noun', morphology)

    def verb(self, string, morphology=None):
        return self(string, 'verb', morphology)

    def adj(self, string, morphology=None):
        return self(string, 'adj', morphology)

    def punct(self, string, morphology=None):
        return self(string, 'punct', morphology)


def lemmatize(string, index, exceptions, rules):
    string = string.lower()
    forms = []
    # TODO: Is this correct? See discussion in Issue #435.
    #if string in index:
    #    forms.append(string)
    forms.extend(exceptions.get(string, []))
    for old, new in rules:
        if string.endswith(old):
            form = string[:len(string) - len(old)] + new
            if form in index or not form.isalpha():
                forms.append(form)
    if not forms:
        forms.append(string)
    return set(forms)


def read_index(fileobj):
    index = set()
    for line in fileobj:
        if line.startswith(' '):
            continue
        pieces = line.split()
        word = pieces[0]
        if word.count('_') == 0:
            index.add(word)
    return index


def read_exc(fileobj):
    exceptions = {}
    for line in fileobj:
        if line.startswith(' '):
            continue
        pieces = line.split()
        exceptions[pieces[0]] = tuple(pieces[1:])
    return exceptions

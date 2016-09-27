from __future__ import unicode_literals, print_function
import codecs
import pathlib

try:
    import ujson as json
except ImportError:
    import json

from .parts_of_speech import NOUN, VERB, ADJ, PUNCT


class Lemmatizer(object):
    @classmethod
    def load(cls, path):
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
        with (path / 'vocab' / 'lemma_rules.json').open() as file_:
            rules = json.load(file_)
        return cls(index, exc, rules)

    def __init__(self, index, exceptions, rules):
        self.index = index
        self.exc = exceptions
        self.rules = rules

    def __call__(self, string, pos, **morphology):
        if pos == NOUN:
            pos = 'noun'
        elif pos == VERB:
            pos = 'verb'
        elif pos == ADJ:
            pos = 'adj'
        elif pos == PUNCT:
            pos = 'punct'
        # See Issue #435 for example of where this logic is requied.
        if self.is_base_form(pos, **morphology):
            return set([string.lower()])
        lemmas = lemmatize(string, self.index.get(pos, {}), self.exc.get(pos, {}), self.rules.get(pos, []))
        return lemmas

    def is_base_form(self, pos, **morphology):
        '''Check whether we're dealing with an uninflected paradigm, so we can
        avoid lemmatization entirely.'''
        if pos == 'noun' and morphology.get('number') == 'sing' and len(morphology) == 1:
            return True
        elif pos == 'verb' and morphology.get('verbform') == 'inf' and len(morphology) == 1:
            return True
        else:
            return False

    def noun(self, string, **morphology):
        return self(string, 'noun', **morphology)

    def verb(self, string, **morphology):
        return self(string, 'verb', **morphology)

    def adj(self, string, **morphology):
        return self(string, 'adj', **morphology)

    def punct(self, string, **morphology):
        return self(string, 'punct', **morphology)


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

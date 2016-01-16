from __future__ import unicode_literals, print_function
from os import path
import codecs

try:
    import ujson as json
except ImportError:
    import json

from .parts_of_speech import NOUN, VERB, ADJ, PUNCT
from .util import get_package


class Lemmatizer(object):
    @classmethod
    def load(cls, via):
        return cls.from_package(get_package(via))

    @classmethod
    def from_package(cls, pkg):
        index = {}
        exc = {}
        for pos in ['adj', 'noun', 'verb']:
            with pkg.open(('wordnet', 'index.%s' % pos), default=None) as file_:
                index[pos] = read_index(file_) if file_ is not None else set()
            with pkg.open(('wordnet', '%s.exc' % pos), default=None) as file_:
                exc[pos] = read_exc(file_) if file_ is not None else {}
        rules = pkg.load_json(('vocab', 'lemma_rules.json'), default={})
        return cls(index, exc, rules)

    def __init__(self, index, exceptions, rules):
        self.index = index
        self.exc = exceptions
        self.rules = rules

    def __call__(self, string, pos):
        if pos == NOUN:
            pos = 'noun'
        elif pos == VERB:
            pos = 'verb'
        elif pos == ADJ:
            pos = 'adj'
        elif pos == PUNCT:
            pos = 'punct'
        lemmas = lemmatize(string, self.index.get(pos, {}), self.exc.get(pos, {}), self.rules.get(pos, []))
        return lemmas

    def noun(self, string):
        return self(string, 'noun')

    def verb(self, string):
        return self(string, 'verb')

    def adj(self, string):
        return self(string, 'adj')

    def punct(self, string):
        return self(string, 'punct')


def lemmatize(string, index, exceptions, rules):
    string = string.lower()
    forms = []
    if string in index:
        forms.append(string)
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

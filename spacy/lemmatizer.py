from __future__ import unicode_literals
from os import path
import codecs

try:
    import ujson as json
except ImportError:
    import json

from .parts_of_speech import NOUN, VERB, ADJ


class Lemmatizer(object):
    @classmethod
    def from_dir(cls, data_dir):
        index = {}
        exc = {}
        for pos in ['adj', 'noun', 'verb']:
            index[pos] = read_index(path.join(data_dir, 'wordnet', 'index.%s' % pos))
            exc[pos] = read_exc(path.join(data_dir, 'wordnet', '%s.exc' % pos))
        if path.exists(path.join(data_dir, 'vocab', 'lemma_rules.json')):
            rules = json.load(open(path.join(data_dir, 'vocab', 'lemma_rules.json')))
        else:
            rules = {}
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
        lemmas = lemmatize(string, self.index.get(pos, {}), self.exc.get(pos, {}), self.rules.get(pos, []))
        return lemmas

    def noun(self, string):
        return self(string, 'noun')

    def verb(self, string):
        return self(string, 'verb')

    def adj(self, string):
        return self(string, 'adj')


def lemmatize(string, index, exceptions, rules):
    string = string.lower()
    forms = []
    if string in index:
        forms.append(string)
    forms.extend(exceptions.get(string, []))
    for old, new in rules:
        if string.endswith(old):
            form = string[:len(string) - len(old)] + new
            if form in index:
                forms.append(form)
    if not forms:
        forms.append(string)
    return set(forms)


def read_index(loc):
    index = set()
    if not path.exists(loc):
        return index
    for line in codecs.open(loc, 'r', 'utf8'):
        if line.startswith(' '):
            continue
        pieces = line.split()
        word = pieces[0]
        if word.count('_') == 0:
            index.add(word)
    return index


def read_exc(loc):
    exceptions = {}
    if not path.exists(loc):
        return exceptions
    for line in codecs.open(loc, 'r', 'utf8'):
        if line.startswith(' '):
            continue
        pieces = line.split()
        exceptions[pieces[0]] = tuple(pieces[1:])
    return exceptions

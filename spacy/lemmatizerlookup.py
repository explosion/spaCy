# coding: utf8
from __future__ import unicode_literals

from .lemmatizer import Lemmatizer


class Lemmatizer(Lemmatizer):
    @classmethod
    def load(cls, path, lookup):
        return cls(lookup or {})

    def __init__(self, lookup):
        self.lookup = lookup

    def __call__(self, string, univ_pos, morphology=None):
        try:
            return set([self.lookup[string]])
        except:
            return set([string])
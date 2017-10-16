# encoding: utf8
from __future__ import unicode_literals, print_function

from ..language import Language
from ..attrs import LANG
from ..tokens import Doc
from .language_data import *


class RussianTokenizer(object):
    _morph = None

    def __init__(self, spacy_tokenizer, cls, nlp=None):
        try:
            from pymorphy2 import MorphAnalyzer
        except ImportError:
            raise ImportError(
                "The Russian tokenizer requires the pymorphy2 library: "
                "try to fix it with "
                "pip install pymorphy2==0.8")

        RussianTokenizer._morph = RussianTokenizer._create_morph(MorphAnalyzer)

        self.vocab = nlp.vocab if nlp else cls.create_vocab(nlp)
        self._spacy_tokenizer = spacy_tokenizer

    def __call__(self, text):
        get_norm = RussianTokenizer._get_norm
        has_space = RussianTokenizer._has_space

        words_with_space_flags = [(get_norm(token), has_space(token, text))
                                  for token in self._spacy_tokenizer(text)]

        words, spaces = map(lambda s: list(s), zip(*words_with_space_flags))

        return Doc(self.vocab, words, spaces)

    @staticmethod
    def _get_word(token):
        return token.lemma_ if len(token.lemma_) > 0 else token.text

    @staticmethod
    def _has_space(token, text):
        pos_after_token = token.idx + len(token.text)
        return pos_after_token < len(text) and text[pos_after_token] == ' '

    @classmethod
    def _get_norm(cls, token):
        return cls._normalize(cls._get_word(token))

    @classmethod
    def _normalize(cls, word):
        return cls._morph.parse(word)[0].normal_form

    @classmethod
    def _create_morph(cls, morph_analyzer_class):
        if not cls._morph:
            cls._morph = morph_analyzer_class()
        return cls._morph


class RussianDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: 'ru'

    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    stop_words = STOP_WORDS

    @classmethod
    def create_tokenizer(cls, nlp=None):
        tokenizer = super(RussianDefaults, cls).create_tokenizer(nlp)
        return RussianTokenizer(tokenizer, cls, nlp)


class Russian(Language):
    lang = 'ru'

    Defaults = RussianDefaults

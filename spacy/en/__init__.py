from __future__ import unicode_literals, print_function

from os import path

from ..language import Language
from . import language_data
from .. import util
from ..lemmatizer import Lemmatizer
from ..vocab import Vocab
from ..tokenizer import Tokenizer


class English(Language):
    lang = 'en'

    class Defaults(Language.Defaults):
        def Vocab(self, lex_attr_getters=True, tag_map=True,
                  lemmatizer=True, serializer_freqs=True, vectors=True):
            if lex_attr_getters is True:
                lex_attr_getters = self.lex_attr_getters
            if tag_map is True:
                tag_map = self.tag_map
            if lemmatizer is True:
                lemmatizer = self.Lemmatizer()
            return Vocab.load(self.path, lex_attr_getters=lex_attr_getters,
                              tag_map=tag_map, lemmatizer=lemmatizer,
                              serializer_freqs=serializer_freqs)

        def Tokenizer(self, vocab, rules=None, prefix_search=None, suffix_search=None,
                infix_finditer=None):
            if rules is None:
                rules = self.tokenizer_exceptions
            if prefix_search is None:
                prefix_search  = util.compile_prefix_regex(self.prefixes).search
            if suffix_search is None:
                suffix_search  = util.compile_suffix_regex(self.suffixes).search
            if infix_finditer is None:
                infix_finditer = util.compile_infix_regex(self.infixes).finditer
            return Tokenizer(vocab, rules=rules,
                    prefix_search=prefix_search, suffix_search=suffix_search,
                    infix_finditer=infix_finditer)

        def Lemmatizer(self):
            return Lemmatizer.load(self.path)
            
        lex_attr_getters = dict(Language.Defaults.lex_attr_getters)

        tokenizer_exceptions = dict(language_data.TOKENIZER_EXCEPTIONS)
        
        prefixes = tuple(language_data.TOKENIZER_PREFIXES)
        
        suffixes = tuple(language_data.TOKENIZER_SUFFIXES)
        
        infixes = tuple(language_data.TOKENIZER_INFIXES)

        tag_map = dict(language_data.TAG_MAP)

        stop_words = set(language_data.STOP_WORDS)


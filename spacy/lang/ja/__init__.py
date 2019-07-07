# encoding: utf8
from __future__ import unicode_literals, print_function

from collections import namedtuple

from ...attrs import LANG
from ...language import Language
from ...tokens import Token
from ...util import get_model_meta
from ...vocab import Vocab
from ...compat import copy_reg

from .stop_words import STOP_WORDS
from .syntax_iterators import SYNTAX_ITERATORS
from .tag_map import TAG_MAP

from .japanese_corrector import JapaneseCorrector
from .sudachi_tokenizer import SudachiTokenizer


ShortUnitWord = namedtuple("ShortUnitWord", ["surface", "lemma", "pos"])

Language.factories['JapaneseCorrector'] = lambda nlp, **cfg: JapaneseCorrector(nlp)

if not Token.get_extension('inf'):
    Token.set_extension('inf', default='')
if not Token.get_extension('bunsetu_bi_label'):
    Token.set_extension('bunsetu_bi_label', default='')
if not Token.get_extension('bunsetu_position_type'):
    Token.set_extension('bunsetu_position_type', default='')


class JapaneseDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda _text: "ja"
    stop_words = STOP_WORDS
    tag_map = TAG_MAP
    syntax_iterators = SYNTAX_ITERATORS
    writing_system = {"direction": "ltr", "has_case": False, "has_letters": False}

    @classmethod
    def create_tokenizer(cls, nlp=None):
        return SudachiTokenizer(nlp)

    @classmethod
    def create_lemmatizer(cls, nlp=None):
        return None


class Japanese(Language):
    lang = "ja"
    Defaults = JapaneseDefaults
    Tokenizer = SudachiTokenizer

    def make_doc(self, text):
        return self.tokenizer(text)


def pickle_japanese(instance):
    return Japanese, tuple()


copy_reg.pickle(Japanese, pickle_japanese)


__all__ = [
    'Japanese',
]

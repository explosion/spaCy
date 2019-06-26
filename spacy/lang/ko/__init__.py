# encoding: utf8
from __future__ import unicode_literals, print_function

import re
from dataclasses import dataclass
# from collections import namedtuple
# from itertools import chain

from .stop_words import STOP_WORDS
from .tag_map import TAG_MAP
from ...attrs import LANG
from ...language import Language
from ...tokens import Doc
from ...compat import copy_reg
from ...util import DummyTokenizer


@dataclass
class Morph:
    surface: str
    lemma: str
    tag: str
    space: bool


def try_mecab_import():
    try:
        from natto import MeCab
        return MeCab
    except ImportError:
        raise ImportError(
            "Korean support requires MeCab in natto-py: "
            "https://natto-py.readthedocs.io"
        )


def resolve_pos(token):
    """If necessary, extract the POS tag of lemma for UD mapping.
    Under Universal Dependencies, sometimes the same Unidic POS tag can
    be mapped differently depending on the literal token or its context
    in the sentence. This function adds information to the POS tag to
    resolve ambiguous mappings.
    """
    # TODO: This is a first take. The rules here are crude approximations.
    # For many of these, full dependencies are needed to properly resolve
    # PoS mappings.
    try:
        pos = TAG_MAP[token.tag]
    except KeyError as identifier:
        pos = TAG_MAP[token.tag.partition('+')[0]]
    return pos


# def check_end(iterables):
#     # check_end(['ABC', 'DEF']) --> (A,False) (B,False) (C,True) (D,False) (E,False) (F,True)

#     for it in iterables:
#         prev = None
#         group_end = False
#         for element in it:
#             if prev is not None:
#                 yield prev, group_end
#             prev = element
#         group_end = True
#         yield prev, group_end


class KoreanTokenizer(DummyTokenizer):
    def __init__(self, cls, nlp=None):
        self.vocab = nlp.vocab if nlp is not None else cls.create_vocab(nlp)
        self.Tokenizer = try_mecab_import()


    def __call__(self, text):
        dtokens = self.detailed_tokens(text)
        words, lemmas, tags, spaces = [], [], [], []
        for x in dtokens:
            words.append(x.surface)
            lemmas.append(x.lemma)
            tags.append(x.tag)
            spaces.append(x.space)
        # breakpoint()
        doc = Doc(self.vocab, words=words, spaces=spaces)
        eunjeon_tags = []
        for token, dtoken in zip(doc, dtokens):
            eunjeon_tags.append(dtoken.tag)
            token.tag_ = dtoken.tag
            token.lemma_ = dtoken.lemma
            token.pos_ = resolve_pos(dtoken.tag)
        doc.user_data["eunjeon_tags"] = eunjeon_tags
        return doc

    def detailed_tokens(self, text):
        with self.Tokenizer() as tokenizer:
            for eojeol in text.split():
                morph, surface, lemma, tag = [None] * 4
                for node in tokenizer.parse(eojeol, as_nodes=True):
                    if surface is not None:
                        yield Morph(surface, lemma, tag, node.is_eos())

                    surface = node.surface
                    # 품사 태그,	의미 부류,	종성 유무,	읽기,	타입,	첫번째 품사,	마지막 품사,	표현
                    feature = node.feature.split(',')
                    tag = feature[0]
                    lemma, sep, remainder = feature[-1].partition('/')
                    breakpoint()
                    if lemma == '*':
                        lemma = surface


class KoreanDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda _text: "ko"
    stop_words = STOP_WORDS
    tag_map = TAG_MAP
    writing_system = {"direction": "ltr", "has_case": False, "has_letters": False}

    @classmethod
    def create_tokenizer(cls, nlp=None):
        return KoreanTokenizer(cls, nlp)


class Korean(Language):
    lang = "ko"
    Defaults = KoreanDefaults

    def make_doc(self, text):
        return self.tokenizer(text)

def pickle_korean(instance):
    return korean, tuple()


copy_reg.pickle(Korean, pickle_korean)
# copy_reg.pickle(Korean, (lambda instance: Korean, tuple()))


__all__ = ["Korean"]

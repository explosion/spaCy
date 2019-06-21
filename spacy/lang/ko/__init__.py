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


# Morph = namedtuple("Morph", ("surface", "pos", "space"))

@dataclass
class Morph:
    surface: str
    pos: str
    space: bool
    

def try_eunjeon_import():
    """pyeunjeon is required for Korean support, so check for it.
    It it's not available blow up and explain how to fix it."""
    try:
        import eunjeon

        return eunjeon
    except ImportError:
        raise ImportError(
            "Korean support requires pyeunjeon MeCab: "
            "https://github.com/koshort/pyeunjeon"
        )


# def resolve_pos(token):
#     """If necessary, add a field to the POS tag for UD mapping.
#     Under Universal Dependencies, sometimes the same Unidic POS tag can
#     be mapped differently depending on the literal token or its context
#     in the sentence. This function adds information to the POS tag to
#     resolve ambiguous mappings.
#     """
#     # TODO: This is a first take. The rules here are crude approximations.
#     # For many of these, full dependencies are needed to properly resolve
#     # PoS mappings.
#     if token.pos == "MM,*,*,*": # 관형사
#         if re.match(r"[こそあど此其彼]の", token.surface):
#             return token.pos + ",DET"
#         if re.match(r"[こそあど此其彼]", token.surface):
#             return token.pos + ",PRON"
#         return token.pos + ",ADJ"
#     return token.pos

def check_end(iterables): 
    # check_end(['ABC', 'DEF']) --> (A,False) (B,False) (C,True) (D,False) (E,False) (F,True) 
     
    for it in iterables: 
        prev = None 
        group_end = False 
        for element in it: 
            if prev is not None: 
                yield prev, group_end 
            prev = element 
        group_end = True 
        yield prev, group_end   

def detailed_tokens(tokenizer, text):
    """Format Mecab output for spacy.Doc"""
    
    morph_group_by_eojeol = check_end(parse(tokenizer.tagger.parse(eojeol)) 
                                      for eojeol in text.split())
    return [Morph(surface, pos, space) for (surface, pos), space in morph_group_by_eojeol]


class KoreanTokenizer(DummyTokenizer):
    def __init__(self, cls, nlp=None):
        self.vocab = nlp.vocab if nlp is not None else cls.create_vocab(nlp)
        self.tokenizer = try_eunjeon_import().Mecab()
        

    def __call__(self, text):
        dtokens = self.tokenizer.pos(text)
        words = [x.surface for x in dtokens]
        spaces = [False] * len(words)
        doc = Doc(self.vocab, words=words, spaces=spaces)
        eunjeon_tags = []
        for token, dtoken in zip(doc, dtokens):
            eunjeon_tags.append(dtoken.pos)
            token.tag_ = dtoken
            token.lemma_ = dtoken.lemma
        doc.user_data["eunjeon_tags"] = eunjeon_tags
        return doc


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


copy_reg.pickle(Korean, lambda instance: Korean, tuple())


__all__ = ["Korean"]

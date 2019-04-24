# encoding: utf8
from __future__ import unicode_literals, print_function

import re
from collections import namedtuple

from .stop_words import STOP_WORDS
from .tag_map import TAG_MAP
from ...attrs import LANG
from ...language import Language
from ...tokens import Doc
from ...compat import copy_reg
from ...util import DummyTokenizer


ShortUnitWord = namedtuple("ShortUnitWord", ["surface", "lemma", "pos"])


def try_mecab_import():
    """Mecab is required for Japanese support, so check for it.
    It it's not available blow up and explain how to fix it."""
    try:
        import MeCab

        return MeCab
    except ImportError:
        raise ImportError(
            "Japanese support requires MeCab: "
            "https://github.com/SamuraiT/mecab-python3"
        )


def resolve_pos(token):
    """If necessary, add a field to the POS tag for UD mapping.
    Under Universal Dependencies, sometimes the same Unidic POS tag can
    be mapped differently depending on the literal token or its context
    in the sentence. This function adds information to the POS tag to
    resolve ambiguous mappings.
    """
    # TODO: This is a first take. The rules here are crude approximations.
    # For many of these, full dependencies are needed to properly resolve
    # PoS mappings.
    if token.pos == "連体詞,*,*,*":
        if re.match(r"[こそあど此其彼]の", token.surface):
            return token.pos + ",DET"
        if re.match(r"[こそあど此其彼]", token.surface):
            return token.pos + ",PRON"
        return token.pos + ",ADJ"
    return token.pos


def detailed_tokens(tokenizer, text):
    """Format Mecab output into a nice data structure, based on Janome."""
    node = tokenizer.parseToNode(text)
    node = node.next  # first node is beginning of sentence and empty, skip it
    words = []
    while node.posid != 0:
        surface = node.surface
        base = surface  # a default value. Updated if available later.
        parts = node.feature.split(",")
        pos = ",".join(parts[0:4])
        if len(parts) > 7:
            # this information is only available for words in the tokenizer
            # dictionary
            base = parts[7]
        words.append(ShortUnitWord(surface, base, pos))
        node = node.next
    return words


class JapaneseTokenizer(DummyTokenizer):
    def __init__(self, cls, nlp=None):
        self.vocab = nlp.vocab if nlp is not None else cls.create_vocab(nlp)
        self.tokenizer = try_mecab_import().Tagger()
        self.tokenizer.parseToNode("")  # see #2901

    def __call__(self, text):
        dtokens = detailed_tokens(self.tokenizer, text)
        words = [x.surface for x in dtokens]
        spaces = [False] * len(words)
        doc = Doc(self.vocab, words=words, spaces=spaces)
        mecab_tags = []
        for token, dtoken in zip(doc, dtokens):
            mecab_tags.append(dtoken.pos)
            token.tag_ = resolve_pos(dtoken)
            token.lemma_ = dtoken.lemma
        doc.user_data["mecab_tags"] = mecab_tags
        return doc


class JapaneseDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda _text: "ja"
    stop_words = STOP_WORDS
    tag_map = TAG_MAP
    writing_system = {"direction": "ltr", "has_case": False, "has_letters": False}

    @classmethod
    def create_tokenizer(cls, nlp=None):
        return JapaneseTokenizer(cls, nlp)


class Japanese(Language):
    lang = "ja"
    Defaults = JapaneseDefaults

    def make_doc(self, text):
        return self.tokenizer(text)


def pickle_japanese(instance):
    return Japanese, tuple()


copy_reg.pickle(Japanese, pickle_japanese)


__all__ = ["Japanese"]

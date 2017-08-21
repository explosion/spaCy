# encoding: utf8
from __future__ import unicode_literals, print_function

from os import path

from ..language import Language, BaseDefaults
from ..tokenizer import Tokenizer
from ..tagger import Tagger
from ..attrs import LANG
from ..tokens import Doc

from .language_data import *

import re
from collections import namedtuple

ShortUnitWord = namedtuple('ShortUnitWord', ['surface', 'base_form', 'part_of_speech'])

def try_mecab_import():
    """Mecab is required for Japanese support, so check for it.

    It it's not available blow up and explain how to fix it."""
    try:
        import MeCab
        return MeCab
    except ImportError:
        raise ImportError("Japanese support requires MeCab: "
                          "https://github.com/SamuraiT/mecab-python3")

class JapaneseTokenizer(object):
    def __init__(self, cls, nlp=None):
        self.vocab = nlp.vocab if nlp is not None else cls.create_vocab(nlp)
        MeCab = try_mecab_import()
        self.tokenizer = MeCab.Tagger()

    def __call__(self, text):
        words = [x.surface for x in detailed_tokens(self.tokenizer, text)]
        return Doc(self.vocab, words=words, spaces=[False]*len(words))

def resolve_pos(token):
    """If necessary, add a field to the POS tag for UD mapping.

    Under Universal Dependencies, sometimes the same Unidic POS tag can
    be mapped differently depending on the literal token or its context
    in the sentence. This function adds information to the POS tag to 
    resolve ambiguous mappings.
    """

    # NOTE: This is a first take. The rules here are crude approximations.
    # For many of these, full dependencies are needed to properly resolve
    # PoS mappings.

    if token.part_of_speech == '連体詞,*,*,*':
        if re.match('^[こそあど此其彼]の', token.surface):
            return token.part_of_speech + ',DET'
        if re.match('^[こそあど此其彼]', token.surface):
            return token.part_of_speech + ',PRON'
        else:
            return token.part_of_speech + ',ADJ'
    return token.part_of_speech

def detailed_tokens(tokenizer, text):
    """Format Mecab output into a nice data structure, based on Janome."""

    node = tokenizer.parseToNode(text)
    node = node.next # first node is beginning of sentence and empty, skip it
    words = []
    while node.posid != 0:
        parts = node.feature.split(',')
        pos = ','.join(parts[0:4])
        reading = parts[6]
        base = parts[7]
        surface = parts[8]

        words.append( ShortUnitWord(surface, base, pos) )
        node = node.next
    return words

class JapaneseTagger(object):
    def __init__(self, vocab):
        MeCab = try_mecab_import()
        self.tagger = Tagger(vocab)
        self.tokenizer = MeCab.Tagger()

    def __call__(self, tokens):
        # two parts to this:
        # 1. get raw JP tags
        # 2. add features to tags as necessary for UD

        # TODO: if the text has been tokenized, this info is already available
        # How to set the data when tokenizing or save it for the tagger to find?

        dtokens = detailed_tokens(self.tokenizer, tokens.text)
        rawtags = list(map(resolve_pos, dtokens))
        self.tagger.tag_from_strings(tokens, rawtags)

class JapaneseDefaults(BaseDefaults):
    tag_map = TAG_MAP

    @classmethod
    def create_tokenizer(cls, nlp=None):
        return JapaneseTokenizer(cls, nlp)

    @classmethod
    def create_tagger(cls, tokenizer):
        return JapaneseTagger(tokenizer.vocab)

class Japanese(Language):
    lang = 'ja'

    Defaults = JapaneseDefaults

    def make_doc(self, text):
        words = [str(t) for t in self.tokenizer(text)]
        doc = Doc(self.vocab, words=words, spaces=[False]*len(words))
        tagger = JapaneseDefaults.create_tagger(self.tokenizer)
        tagger(doc)
        return doc

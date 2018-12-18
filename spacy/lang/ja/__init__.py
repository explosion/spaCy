# encoding: utf8
from __future__ import unicode_literals, print_function

from ...language import Language
from ...attrs import LANG
from ...tokens import Doc, Token
from ...tokenizer import Tokenizer
from ... import util
from .tag_map import TAG_MAP

import re
from collections import namedtuple


ShortUnitWord = namedtuple("ShortUnitWord", ["surface", "lemma", "pos"])


def try_mecab_import():
    """Mecab is required for Japanese support, so check for it.

    It it's not available blow up and explain how to fix it."""
    try:
        import MeCab

        # XXX Is this the right place for this?
        Token.set_extension("mecab_tag", default=None)
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

    # NOTE: This is a first take. The rules here are crude approximations.
    # For many of these, full dependencies are needed to properly resolve
    # PoS mappings.

    if token.pos == "連体詞,*,*,*":
        if re.match("^[こそあど此其彼]の", token.surface):
            return token.pos + ",DET"
        if re.match("^[こそあど此其彼]", token.surface):
            return token.pos + ",PRON"
        else:
            return token.pos + ",ADJ"
    return token.pos


def detailed_tokens(tokenizer, text):
    """Format Mecab output into a nice data structure, based on Janome."""
    tokenizer.parse(text)
    node = tokenizer.parseToNode(text)
    node = node.next  # first node is beginning of sentence and empty, skip it
    words = []
    while node.posid != 0:
        surface = node.surface
        base = surface  # a default value. Updated if available later.
        parts = node.feature.split(",")
        pos = ",".join(parts[0:4])

        if len(parts) > 7:
            # this information is only available for words in the tokenizer dictionary
            base = parts[7]

        words.append(ShortUnitWord(surface, base, pos))
        node = node.next
    return words


class JapaneseTokenizer(object):
    def __init__(self, cls, nlp=None):
        self.vocab = nlp.vocab if nlp is not None else cls.create_vocab(nlp)

        MeCab = try_mecab_import()
        self.tokenizer = MeCab.Tagger()
        self.tokenizer.parseToNode("")  # see #2901

    def __call__(self, text):
        dtokens = detailed_tokens(self.tokenizer, text)
        words = [x.surface for x in dtokens]
        doc = Doc(self.vocab, words=words, spaces=[False] * len(words))
        for token, dtoken in zip(doc, dtokens):
            token._.mecab_tag = dtoken.pos
            token.tag_ = resolve_pos(dtoken)
            token.lemma_ = dtoken.lemma
        return doc

    # add dummy methods for to_bytes, from_bytes, to_disk and from_disk to
    # allow serialization (see #1557)
    def to_bytes(self, **exclude):
        return b""

    def from_bytes(self, bytes_data, **exclude):
        return self

    def to_disk(self, path, **exclude):
        return None

    def from_disk(self, path, **exclude):
        return self


class JapaneseCharacterSegmenter(object):
    def __init__(self, vocab):
        self.vocab = vocab
        self._presegmenter = self._make_presegmenter(self.vocab)

    def _make_presegmenter(self, vocab):
        rules = Japanese.Defaults.tokenizer_exceptions
        token_match = Japanese.Defaults.token_match
        prefix_search = (
            util.compile_prefix_regex(Japanese.Defaults.prefixes).search
            if Japanese.Defaults.prefixes
            else None
        )
        suffix_search = (
            util.compile_suffix_regex(Japanese.Defaults.suffixes).search
            if Japanese.Defaults.suffixes
            else None
        )
        infix_finditer = (
            util.compile_infix_regex(Japanese.Defaults.infixes).finditer
            if Japanese.Defaults.infixes
            else None
        )
        return Tokenizer(
            vocab,
            rules=rules,
            prefix_search=prefix_search,
            suffix_search=suffix_search,
            infix_finditer=infix_finditer,
            token_match=token_match,
        )

    def __call__(self, text):
        words = []
        spaces = []
        doc = self._presegmenter(text)
        for token in doc:
            words.extend(list(token.text))
            spaces.extend([False] * len(token.text))
            spaces[-1] = bool(token.whitespace_)
        return Doc(self.vocab, words=words, spaces=spaces)


class JapaneseDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda text: "ja"
    tag_map = TAG_MAP
    use_janome = True

    @classmethod
    def create_tokenizer(cls, nlp=None):
        if cls.use_janome:
            return JapaneseTokenizer(cls, nlp)
        else:
            return JapaneseCharacterSegmenter(nlp.vocab)


class Japanese(Language):
    lang = "ja"
    Defaults = JapaneseDefaults
    Tokenizer = JapaneseTokenizer

    def make_doc(self, text):
        return self.tokenizer(text)


__all__ = ["Japanese"]

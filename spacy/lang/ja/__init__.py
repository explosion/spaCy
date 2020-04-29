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

# Handling for multiple spaces in a row is somewhat awkward, this simplifies
# the flow by creating a dummy with the same interface.
DummyNode = namedtuple("DummyNode", ["surface", "pos", "feature"])
DummyNodeFeatures = namedtuple("DummyNodeFeatures", ["lemma"])
DummySpace = DummyNode(" ", " ", DummyNodeFeatures(" "))


def try_fugashi_import():
    """Fugashi is required for Japanese support, so check for it.
    It it's not available blow up and explain how to fix it."""
    try:
        import fugashi

        return fugashi
    except ImportError:
        raise ImportError(
            "Japanese support requires Fugashi: " "https://github.com/polm/fugashi"
        )


def resolve_pos(token, next_token):
    """If necessary, add a field to the POS tag for UD mapping.
    Under Universal Dependencies, sometimes the same Unidic POS tag can
    be mapped differently depending on the literal token or its context
    in the sentence. This function adds information to the POS tag to
    resolve ambiguous mappings.
    """

    # this is only used for consecutive ascii spaces
    if token.surface == " ":
        return "空白"

    # Some tokens have their UD tag decided based on the POS of the following
    # token.
    next_pos = None
    if next_token:
        next_pos = next_token.pos

    if token.pos == "連体詞,*,*,*":
        if re.match(r"[こそあど此其彼]の", token.surface):
            return token.pos + ",DET"
        elif re.match(r"[こそあど此其彼]", token.surface):
            return token.pos + ",PRON"
        else:
            return token.pos + ",ADJ"

    if token.feature.lemma == '為る' and token.pos == '動詞,非自立可能,*,*':
        return token.pos + ',AUX'

    if token.pos == "名詞,普通名詞,サ変可能,*":
        if next_pos == '動詞,非自立可能,*,*':
            return token.pos + ',VERB'
        else:
            return token.pos + ',NOUN'

    if token.pos == '名詞,普通名詞,サ変形状詞可能,*':
        if next_pos == '動詞,非自立可能,*,*':
            return token.pos + ',VERB'
        elif next_pos == '助動詞,*,*,*' or next_pos.find('形状詞') >= 0:
            return token.pos + ',ADJ'
        else:
            return token.pos + ',NOUN'

    return token.pos


def get_words_and_spaces(tokenizer, text):
    """Get the individual tokens that make up the sentence and handle white space.

    Japanese doesn't usually use white space, and MeCab's handling of it for
    multiple spaces in a row is somewhat awkward.
    """

    tokens = tokenizer.parseToNodeList(text)

    words = []
    spaces = []
    for token in tokens:
        # If there's more than one space, spaces after the first become tokens
        for ii in range(len(token.white_space) - 1):
            words.append(DummySpace)
            spaces.append(False)

        words.append(token)
        spaces.append(bool(token.white_space))
    return words, spaces


class JapaneseTokenizer(DummyTokenizer):
    def __init__(self, cls, nlp=None):
        self.vocab = nlp.vocab if nlp is not None else cls.create_vocab(nlp)
        self.tokenizer = try_fugashi_import().Tagger()
        self.tokenizer.parseToNodeList("")  # see #2901

    def __call__(self, text):
        dtokens, spaces = get_words_and_spaces(self.tokenizer, text)
        words = [x.surface for x in dtokens]
        doc = Doc(self.vocab, words=words, spaces=spaces)
        unidic_tags = []
        for ii, (token, dtoken) in enumerate(zip(doc, dtokens)):
            ntoken = dtokens[ii+1] if ii+1 < len(dtokens) else None
            unidic_tags.append(dtoken.pos)
            token.tag_ = resolve_pos(dtoken, ntoken)

            # if there's no lemma info (it's an unk) just use the surface
            token.lemma_ = dtoken.feature.lemma or dtoken.surface
        doc.user_data["unidic_tags"] = unidic_tags
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

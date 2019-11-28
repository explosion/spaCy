# coding: utf8
from __future__ import unicode_literals

from ...attrs import LANG
from ...language import Language
from ...tokens import Doc
from ...util import DummyTokenizer
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from .lex_attrs import LEX_ATTRS
from .stop_words import STOP_WORDS
from .tag_map import TAG_MAP


def try_jieba_import(use_jieba):
    try:
        import jieba

        return jieba
    except ImportError:
        if use_jieba:
            msg = (
                "Jieba not installed. Either set Chinese.use_jieba = False, "
                "or install it https://github.com/fxsjy/jieba"
            )
            raise ImportError(msg)


class ChineseTokenizer(DummyTokenizer):
    def __init__(self, cls, nlp=None):
        self.vocab = nlp.vocab if nlp is not None else cls.create_vocab(nlp)
        self.use_jieba = cls.use_jieba
        self.jieba_seg = try_jieba_import(self.use_jieba)
        self.tokenizer = Language.Defaults().create_tokenizer(nlp)

    def __call__(self, text):
        # use jieba
        if self.use_jieba:
            jieba_words = list(
                [x for x in self.jieba_seg.cut(text, cut_all=False) if x]
            )
            words = [jieba_words[0]]
            spaces = [False]
            for i in range(1, len(jieba_words)):
                word = jieba_words[i]
                if word.isspace():
                    # second token in adjacent whitespace following a
                    # non-space token
                    if spaces[-1]:
                        words.append(word)
                        spaces.append(False)
                    # first space token following non-space token
                    elif word == " " and not words[-1].isspace():
                        spaces[-1] = True
                    # token is non-space whitespace or any whitespace following
                    # a whitespace token
                    else:
                        # extend previous whitespace token with more whitespace
                        if words[-1].isspace():
                            words[-1] += word
                        # otherwise it's a new whitespace token
                        else:
                            words.append(word)
                            spaces.append(False)
                else:
                    words.append(word)
                    spaces.append(False)
            return Doc(self.vocab, words=words, spaces=spaces)

        # split into individual characters
        words = []
        spaces = []
        for token in self.tokenizer(text):
            if token.text.isspace():
                words.append(token.text)
                spaces.append(False)
            else:
                words.extend(list(token.text))
                spaces.extend([False] * len(token.text))
                spaces[-1] = bool(token.whitespace_)
        return Doc(self.vocab, words=words, spaces=spaces)


class ChineseDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[LANG] = lambda text: "zh"
    tokenizer_exceptions = BASE_EXCEPTIONS
    stop_words = STOP_WORDS
    tag_map = TAG_MAP
    writing_system = {"direction": "ltr", "has_case": False, "has_letters": False}
    use_jieba = True

    @classmethod
    def create_tokenizer(cls, nlp=None):
        return ChineseTokenizer(cls, nlp)


class Chinese(Language):
    lang = "zh"
    Defaults = ChineseDefaults  # override defaults

    def make_doc(self, text):
        return self.tokenizer(text)


__all__ = ["Chinese"]

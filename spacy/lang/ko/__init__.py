# encoding: utf8
from __future__ import unicode_literals, print_function

from .stop_words import STOP_WORDS
from .tag_map import TAG_MAP
from ...attrs import LANG
from ...language import Language
from ...tokens import Doc
from ...compat import copy_reg
from ...util import DummyTokenizer


def try_mecab_import():
    try:
        from natto import MeCab

        return MeCab
    except ImportError:
        raise ImportError(
            "Korean support requires [mecab-ko](https://bitbucket.org/eunjeon/mecab-ko/src/master/README.md), "
            "[mecab-ko-dic](https://bitbucket.org/eunjeon/mecab-ko-dic), "
            "and [natto-py](https://github.com/buruzaemon/natto-py)"
        )


# fmt: on


def check_spaces(text, tokens):
    prev_end = -1
    start = 0
    for token in tokens:
        idx = text.find(token, start)
        if prev_end > 0:
            yield prev_end != idx
        prev_end = idx + len(token)
        start = prev_end
    if start > 0:
        yield False


class KoreanTokenizer(DummyTokenizer):
    def __init__(self, cls, nlp=None):
        self.vocab = nlp.vocab if nlp is not None else cls.create_vocab(nlp)
        MeCab = try_mecab_import()
        self.mecab_tokenizer = MeCab("-F%f[0],%f[7]")

    def __del__(self):
        self.mecab_tokenizer.__del__()

    def __call__(self, text):
        dtokens = list(self.detailed_tokens(text))
        surfaces = [dt["surface"] for dt in dtokens]
        doc = Doc(self.vocab, words=surfaces, spaces=list(check_spaces(text, surfaces)))
        for token, dtoken in zip(doc, dtokens):
            first_tag, sep, eomi_tags = dtoken["tag"].partition("+")
            token.tag_ = first_tag  # stem(어간) or pre-final(선어말 어미)
            token.lemma_ = dtoken["lemma"]
        doc.user_data["full_tags"] = [dt["tag"] for dt in dtokens]
        return doc

    def detailed_tokens(self, text):
        # 품사 태그(POS)[0], 의미 부류(semantic class)[1],	종성 유무(jongseong)[2], 읽기(reading)[3],
        # 타입(type)[4], 첫번째 품사(start pos)[5],	마지막 품사(end pos)[6], 표현(expression)[7], *
        for node in self.mecab_tokenizer.parse(text, as_nodes=True):
            if node.is_eos():
                break
            surface = node.surface
            feature = node.feature
            tag, _, expr = feature.partition(",")
            lemma, _, remainder = expr.partition("/")
            if lemma == "*":
                lemma = surface
            yield {"surface": surface, "lemma": lemma, "tag": tag}


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
    return Korean, tuple()


copy_reg.pickle(Korean, pickle_korean)

__all__ = ["Korean"]

from thinc.api import Config

from .stop_words import STOP_WORDS
from .tag_map import TAG_MAP
from ...attrs import LANG
from ...language import Language
from ...tokens import Doc
from ...compat import copy_reg
from ...util import DummyTokenizer, registry


DEFAULT_CONFIG = """
[nlp]
lang = "ko"

[nlp.tokenizer]
@tokenizers = "spacy.KoreanTokenizer.v1"

[nlp.writing_system]
direction = "ltr"
has_case = false
has_letters = false
"""


@registry.tokenizers("spacy.KoreanTokenizer.v1")
def create_korean_tokenizer():
    def korean_tokenizer_factory(nlp):
        return KoreanTokenizer(nlp)

    return korean_tokenizer_factory


class KoreanTokenizer(DummyTokenizer):
    def __init__(self, nlp: Language) -> None:
        self.vocab = nlp.vocab
        self.Tokenizer = try_mecab_import()

    def __call__(self, text: str) -> Doc:
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
        with self.Tokenizer("-F%f[0],%f[7]") as tokenizer:
            for node in tokenizer.parse(text, as_nodes=True):
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


class Korean(Language):
    lang = "ko"
    Defaults = KoreanDefaults
    default_config = Config().from_str(DEFAULT_CONFIG)


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


def pickle_korean(instance):
    return Korean, tuple()


copy_reg.pickle(Korean, pickle_korean)

__all__ = ["Korean"]

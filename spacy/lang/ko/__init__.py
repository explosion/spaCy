from typing import Any, Dict, Iterator

from ...language import BaseDefaults, Language
from ...scorer import Scorer
from ...symbols import POS, X
from ...tokens import Doc
from ...training import validate_examples
from ...util import DummyTokenizer, load_config_from_str, registry
from ...vocab import Vocab
from .lex_attrs import LEX_ATTRS
from .punctuation import TOKENIZER_INFIXES
from .stop_words import STOP_WORDS
from .tag_map import TAG_MAP

DEFAULT_CONFIG = """
[nlp]

[nlp.tokenizer]
@tokenizers = "spacy.ko.KoreanTokenizer"
"""


@registry.tokenizers("spacy.ko.KoreanTokenizer")
def create_tokenizer():
    def korean_tokenizer_factory(nlp):
        return KoreanTokenizer(nlp.vocab)

    return korean_tokenizer_factory


class KoreanTokenizer(DummyTokenizer):
    def __init__(self, vocab: Vocab):
        self.vocab = vocab
        self._mecab = try_mecab_import()  # type: ignore[func-returns-value]
        self._mecab_tokenizer = None

    @property
    def mecab_tokenizer(self):
        # This is a property so that initializing a pipeline with blank:ko is
        # possible without actually requiring mecab-ko, e.g. to run
        # `spacy init vectors ko` for a pipeline that will have a different
        # tokenizer in the end. The languages need to match for the vectors
        # to be imported and there's no way to pass a custom config to
        # `init vectors`.
        if self._mecab_tokenizer is None:
            self._mecab_tokenizer = self._mecab("-F%f[0],%f[7]")
        return self._mecab_tokenizer

    def __reduce__(self):
        return KoreanTokenizer, (self.vocab,)

    def __call__(self, text: str) -> Doc:
        dtokens = list(self.detailed_tokens(text))
        surfaces = [dt["surface"] for dt in dtokens]
        doc = Doc(self.vocab, words=surfaces, spaces=list(check_spaces(text, surfaces)))
        for token, dtoken in zip(doc, dtokens):
            first_tag, sep, eomi_tags = dtoken["tag"].partition("+")
            token.tag_ = first_tag  # stem(어간) or pre-final(선어말 어미)
            if token.tag_ in TAG_MAP:
                token.pos = TAG_MAP[token.tag_][POS]
            else:
                token.pos = X
            token.lemma_ = dtoken["lemma"]
        doc.user_data["full_tags"] = [dt["tag"] for dt in dtokens]
        return doc

    def detailed_tokens(self, text: str) -> Iterator[Dict[str, Any]]:
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

    def score(self, examples):
        validate_examples(examples, "KoreanTokenizer.score")
        return Scorer.score_tokenization(examples)


class KoreanDefaults(BaseDefaults):
    config = load_config_from_str(DEFAULT_CONFIG)
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS
    writing_system = {"direction": "ltr", "has_case": False, "has_letters": False}
    infixes = TOKENIZER_INFIXES


class Korean(Language):
    lang = "ko"
    Defaults = KoreanDefaults


def try_mecab_import() -> None:
    try:
        from natto import MeCab

        return MeCab
    except ImportError:
        raise ImportError(
            'The Korean tokenizer ("spacy.ko.KoreanTokenizer") requires '
            "[mecab-ko](https://bitbucket.org/eunjeon/mecab-ko/src/master/README.md), "
            "[mecab-ko-dic](https://bitbucket.org/eunjeon/mecab-ko-dic), "
            "and [natto-py](https://github.com/buruzaemon/natto-py)"
        ) from None


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


__all__ = ["Korean"]

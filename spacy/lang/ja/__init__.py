import re
from collections import namedtuple
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union

import srsly
from thinc.api import Model

from ... import util
from ...errors import Errors
from ...language import BaseDefaults, Language
from ...pipeline import Morphologizer
from ...pipeline.morphologizer import DEFAULT_MORPH_MODEL
from ...scorer import Scorer
from ...symbols import POS
from ...tokens import Doc, MorphAnalysis
from ...training import validate_examples
from ...util import DummyTokenizer, load_config_from_str, registry
from ...vocab import Vocab
from .stop_words import STOP_WORDS
from .syntax_iterators import SYNTAX_ITERATORS
from .tag_bigram_map import TAG_BIGRAM_MAP
from .tag_map import TAG_MAP
from .tag_orth_map import TAG_ORTH_MAP

DEFAULT_CONFIG = """
[nlp]

[nlp.tokenizer]
@tokenizers = "spacy.ja.JapaneseTokenizer"
split_mode = null
"""


@registry.tokenizers("spacy.ja.JapaneseTokenizer")
def create_tokenizer(split_mode: Optional[str] = None):
    def japanese_tokenizer_factory(nlp):
        return JapaneseTokenizer(nlp.vocab, split_mode=split_mode)

    return japanese_tokenizer_factory


class JapaneseTokenizer(DummyTokenizer):
    def __init__(self, vocab: Vocab, split_mode: Optional[str] = None) -> None:
        self.vocab = vocab
        self.split_mode = split_mode
        self.tokenizer = try_sudachi_import(self.split_mode)
        # if we're using split mode A we don't need subtokens
        self.need_subtokens = not (split_mode is None or split_mode == "A")

    def __reduce__(self):
        return JapaneseTokenizer, (self.vocab, self.split_mode)

    def __call__(self, text: str) -> Doc:
        # convert sudachipy.morpheme.Morpheme to DetailedToken and merge continuous spaces
        sudachipy_tokens = self.tokenizer.tokenize(text)
        dtokens = self._get_dtokens(sudachipy_tokens)
        dtokens, spaces = get_dtokens_and_spaces(dtokens, text)

        # create Doc with tag bi-gram based part-of-speech identification rules
        words, tags, inflections, lemmas, norms, readings, sub_tokens_list = (
            zip(*dtokens) if dtokens else [[]] * 7
        )
        sub_tokens_list = list(sub_tokens_list)
        doc = Doc(self.vocab, words=words, spaces=spaces)
        next_pos = None  # for bi-gram rules
        for idx, (token, dtoken) in enumerate(zip(doc, dtokens)):
            token.tag_ = dtoken.tag
            if next_pos:  # already identified in previous iteration
                token.pos = next_pos
                next_pos = None
            else:
                token.pos, next_pos = resolve_pos(
                    token.orth_,
                    dtoken.tag,
                    tags[idx + 1] if idx + 1 < len(tags) else None,
                )
            # if there's no lemma info (it's an unk) just use the surface
            token.lemma_ = dtoken.lemma if dtoken.lemma else dtoken.surface
            morph = {}
            if dtoken.inf:
                # it's normal for this to be empty for non-inflecting types
                morph["Inflection"] = dtoken.inf
            token.norm_ = dtoken.norm
            if dtoken.reading:
                # punctuation is its own reading, but we don't want values like
                # "=" here
                morph["Reading"] = re.sub("[=|]", "_", dtoken.reading)
            token.morph = MorphAnalysis(self.vocab, morph)
        if self.need_subtokens:
            doc.user_data["sub_tokens"] = sub_tokens_list
        return doc

    def _get_dtokens(self, sudachipy_tokens, need_sub_tokens: bool = True):
        sub_tokens_list = (
            self._get_sub_tokens(sudachipy_tokens) if need_sub_tokens else None
        )
        dtokens = [
            DetailedToken(
                token.surface(),  # orth
                "-".join([xx for xx in token.part_of_speech()[:4] if xx != "*"]),  # tag
                ";".join([xx for xx in token.part_of_speech()[4:] if xx != "*"]),  # inf
                token.dictionary_form(),  # lemma
                token.normalized_form(),
                token.reading_form(),
                sub_tokens_list[idx]
                if sub_tokens_list
                else None,  # user_data['sub_tokens']
            )
            for idx, token in enumerate(sudachipy_tokens)
            if len(token.surface()) > 0
            # remove empty tokens which can be produced with characters like … that
        ]
        # Sudachi normalizes internally and outputs each space char as a token.
        # This is the preparation for get_dtokens_and_spaces() to merge the continuous space tokens
        return [
            t
            for idx, t in enumerate(dtokens)
            if idx == 0
            or not t.surface.isspace()
            or t.tag != "空白"
            or not dtokens[idx - 1].surface.isspace()
            or dtokens[idx - 1].tag != "空白"
        ]

    def _get_sub_tokens(self, sudachipy_tokens):
        # do nothing for default split mode
        if not self.need_subtokens:
            return None

        sub_tokens_list = []  # list of (list of list of DetailedToken | None)
        for token in sudachipy_tokens:
            sub_a = token.split(self.tokenizer.SplitMode.A)
            if len(sub_a) == 1:  # no sub tokens
                sub_tokens_list.append(None)
            elif self.split_mode == "B":
                sub_tokens_list.append([self._get_dtokens(sub_a, False)])
            else:  # "C"
                sub_b = token.split(self.tokenizer.SplitMode.B)
                if len(sub_a) == len(sub_b):
                    dtokens = self._get_dtokens(sub_a, False)
                    sub_tokens_list.append([dtokens, dtokens])
                else:
                    sub_tokens_list.append(
                        [
                            self._get_dtokens(sub_a, False),
                            self._get_dtokens(sub_b, False),
                        ]
                    )
        return sub_tokens_list

    def score(self, examples):
        validate_examples(examples, "JapaneseTokenizer.score")
        return Scorer.score_tokenization(examples)

    def _get_config(self) -> Dict[str, Any]:
        return {"split_mode": self.split_mode}

    def _set_config(self, config: Dict[str, Any] = {}) -> None:
        self.split_mode = config.get("split_mode", None)

    def to_bytes(self, **kwargs) -> bytes:
        serializers = {"cfg": lambda: srsly.json_dumps(self._get_config())}
        return util.to_bytes(serializers, [])

    def from_bytes(self, data: bytes, **kwargs) -> "JapaneseTokenizer":
        deserializers = {"cfg": lambda b: self._set_config(srsly.json_loads(b))}
        util.from_bytes(data, deserializers, [])
        self.tokenizer = try_sudachi_import(self.split_mode)
        return self

    def to_disk(self, path: Union[str, Path], **kwargs) -> None:
        path = util.ensure_path(path)
        serializers = {"cfg": lambda p: srsly.write_json(p, self._get_config())}
        util.to_disk(path, serializers, [])

    def from_disk(self, path: Union[str, Path], **kwargs) -> "JapaneseTokenizer":
        path = util.ensure_path(path)
        serializers = {"cfg": lambda p: self._set_config(srsly.read_json(p))}
        util.from_disk(path, serializers, [])
        self.tokenizer = try_sudachi_import(self.split_mode)
        return self


class JapaneseDefaults(BaseDefaults):
    config = load_config_from_str(DEFAULT_CONFIG)
    stop_words = STOP_WORDS
    syntax_iterators = SYNTAX_ITERATORS
    writing_system = {"direction": "ltr", "has_case": False, "has_letters": False}


class Japanese(Language):
    lang = "ja"
    Defaults = JapaneseDefaults


@Japanese.factory(
    "morphologizer",
    assigns=["token.morph", "token.pos"],
    default_config={
        "model": DEFAULT_MORPH_MODEL,
        "overwrite": True,
        "extend": True,
        "scorer": {"@scorers": "spacy.morphologizer_scorer.v1"},
    },
    default_score_weights={
        "pos_acc": 0.5,
        "morph_micro_f": 0.5,
        "morph_per_feat": None,
    },
)
def make_morphologizer(
    nlp: Language,
    model: Model,
    name: str,
    overwrite: bool,
    extend: bool,
    scorer: Optional[Callable],
):
    return Morphologizer(
        nlp.vocab, model, name, overwrite=overwrite, extend=extend, scorer=scorer
    )


# Hold the attributes we need with convenient names
DetailedToken = namedtuple(
    "DetailedToken", ["surface", "tag", "inf", "lemma", "norm", "reading", "sub_tokens"]
)


def try_sudachi_import(split_mode="A"):
    """SudachiPy is required for Japanese support, so check for it.
    It it's not available blow up and explain how to fix it.
    split_mode should be one of these values: "A", "B", "C", None->"A"."""
    try:
        from sudachipy import dictionary, tokenizer

        split_mode = {
            None: tokenizer.Tokenizer.SplitMode.A,
            "A": tokenizer.Tokenizer.SplitMode.A,
            "B": tokenizer.Tokenizer.SplitMode.B,
            "C": tokenizer.Tokenizer.SplitMode.C,
        }[split_mode]
        tok = dictionary.Dictionary().create(mode=split_mode)
        return tok
    except ImportError:
        raise ImportError(
            "Japanese support requires SudachiPy and SudachiDict-core "
            "(https://github.com/WorksApplications/SudachiPy). "
            "Install with `pip install sudachipy sudachidict_core` or "
            "install spaCy with `pip install spacy[ja]`."
        ) from None


def resolve_pos(orth, tag, next_tag):
    """If necessary, add a field to the POS tag for UD mapping.
    Under Universal Dependencies, sometimes the same Unidic POS tag can
    be mapped differently depending on the literal token or its context
    in the sentence. This function returns resolved POSs for both token
    and next_token by tuple.
    """

    # Some tokens have their UD tag decided based on the POS of the following
    # token.

    # apply orth based mapping
    if tag in TAG_ORTH_MAP:
        orth_map = TAG_ORTH_MAP[tag]
        if orth in orth_map:
            return orth_map[orth], None  # current_pos, next_pos

    # apply tag bi-gram mapping
    if next_tag:
        tag_bigram = tag, next_tag
        if tag_bigram in TAG_BIGRAM_MAP:
            current_pos, next_pos = TAG_BIGRAM_MAP[tag_bigram]
            if current_pos is None:  # apply tag uni-gram mapping for current_pos
                return (
                    TAG_MAP[tag][POS],
                    next_pos,
                )  # only next_pos is identified by tag bi-gram mapping
            else:
                return current_pos, next_pos

    # apply tag uni-gram mapping
    return TAG_MAP[tag][POS], None


def get_dtokens_and_spaces(dtokens, text, gap_tag="空白"):
    # Compare the content of tokens and text, first
    words = [x.surface for x in dtokens]
    if "".join("".join(words).split()) != "".join(text.split()):
        raise ValueError(Errors.E194.format(text=text, words=words))

    text_dtokens = []
    text_spaces = []
    text_pos = 0
    # handle empty and whitespace-only texts
    if len(words) == 0:
        return text_dtokens, text_spaces
    elif len([word for word in words if not word.isspace()]) == 0:
        assert text.isspace()
        text_dtokens = [DetailedToken(text, gap_tag, "", text, text, None, None)]
        text_spaces = [False]
        return text_dtokens, text_spaces

    # align words and dtokens by referring text, and insert gap tokens for the space char spans
    for i, (word, dtoken) in enumerate(zip(words, dtokens)):
        # skip all space tokens
        if word.isspace():
            continue
        try:
            word_start = text[text_pos:].index(word)
        except ValueError:
            raise ValueError(Errors.E194.format(text=text, words=words)) from None

        # space token
        if word_start > 0:
            w = text[text_pos : text_pos + word_start]
            text_dtokens.append(DetailedToken(w, gap_tag, "", w, w, None, None))
            text_spaces.append(False)
            text_pos += word_start

        # content word
        text_dtokens.append(dtoken)
        text_spaces.append(False)
        text_pos += len(word)
        # poll a space char after the word
        if i + 1 < len(dtokens) and dtokens[i + 1].surface == " ":
            text_spaces[-1] = True
            text_pos += 1

    # trailing space token
    if text_pos < len(text):
        w = text[text_pos:]
        text_dtokens.append(DetailedToken(w, gap_tag, "", w, w, None, None))
        text_spaces.append(False)

    return text_dtokens, text_spaces


__all__ = ["Japanese"]

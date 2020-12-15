# encoding: utf8
from __future__ import unicode_literals, print_function

import srsly
from collections import namedtuple, OrderedDict

from .stop_words import STOP_WORDS
from .syntax_iterators import SYNTAX_ITERATORS
from .tag_map import TAG_MAP
from .tag_orth_map import TAG_ORTH_MAP
from .tag_bigram_map import TAG_BIGRAM_MAP
from ...attrs import LANG
from ...compat import copy_reg
from ...errors import Errors
from ...language import Language
from ...symbols import POS
from ...tokens import Doc
from ...util import DummyTokenizer
from ... import util


# Hold the attributes we need with convenient names
DetailedToken = namedtuple("DetailedToken", ["surface", "tag", "inf", "lemma", "reading", "sub_tokens"])


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
        tok = dictionary.Dictionary().create(
            mode=split_mode
        )
        return tok
    except ImportError:
        raise ImportError(
            "Japanese support requires SudachiPy and SudachiDict-core "
            "(https://github.com/WorksApplications/SudachiPy). "
            "Install with `pip install sudachipy sudachidict_core` or "
            "install spaCy with `pip install spacy[ja]`."
        )


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
                return TAG_MAP[tag][POS], next_pos  # only next_pos is identified by tag bi-gram mapping
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
        text_dtokens = [DetailedToken(text, gap_tag, '', text, None, None)]
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
            raise ValueError(Errors.E194.format(text=text, words=words))

        # space token
        if word_start > 0:
            w = text[text_pos:text_pos + word_start]
            text_dtokens.append(DetailedToken(w, gap_tag, '', w, None, None))
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
        text_dtokens.append(DetailedToken(w, gap_tag, '', w, None, None))
        text_spaces.append(False)

    return text_dtokens, text_spaces


class JapaneseTokenizer(DummyTokenizer):
    def __init__(self, cls, nlp=None, config={}):
        self.vocab = nlp.vocab if nlp is not None else cls.create_vocab(nlp)
        self.split_mode = config.get("split_mode", None)
        self.tokenizer = try_sudachi_import(self.split_mode)

    def __call__(self, text):
        # convert sudachipy.morpheme.Morpheme to DetailedToken and merge continuous spaces
        sudachipy_tokens = self.tokenizer.tokenize(text)
        dtokens = self._get_dtokens(sudachipy_tokens)
        dtokens, spaces = get_dtokens_and_spaces(dtokens, text)

        # create Doc with tag bi-gram based part-of-speech identification rules
        words, tags, inflections, lemmas, readings, sub_tokens_list = zip(*dtokens) if dtokens else [[]] * 6
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
                    tags[idx + 1] if idx + 1 < len(tags) else None
                )
            # if there's no lemma info (it's an unk) just use the surface
            token.lemma_ = dtoken.lemma if dtoken.lemma else dtoken.surface

        doc.user_data["inflections"] = inflections
        doc.user_data["reading_forms"] = readings
        doc.user_data["sub_tokens"] = sub_tokens_list
        doc.is_tagged = True

        return doc

    def _get_dtokens(self, sudachipy_tokens, need_sub_tokens=True):
        sub_tokens_list = self._get_sub_tokens(sudachipy_tokens) if need_sub_tokens else None
        dtokens = [
            DetailedToken(
                token.surface(),  # orth
                '-'.join([xx for xx in token.part_of_speech()[:4] if xx != '*']),  # tag
                ','.join([xx for xx in token.part_of_speech()[4:] if xx != '*']),  # inf
                token.dictionary_form(),  # lemma
                token.reading_form(),  # user_data['reading_forms']
                sub_tokens_list[idx] if sub_tokens_list else None,  # user_data['sub_tokens']
            ) for idx, token in enumerate(sudachipy_tokens) if len(token.surface()) > 0
            # remove empty tokens which can be produced with characters like … that
        ]
        # Sudachi normalizes internally and outputs each space char as a token.
        # This is the preparation for get_dtokens_and_spaces() to merge the continuous space tokens
        return [
            t for idx, t in enumerate(dtokens) if
            idx == 0 or
            not t.surface.isspace() or t.tag != '空白' or
            not dtokens[idx - 1].surface.isspace() or dtokens[idx - 1].tag != '空白'
        ]

    def _get_sub_tokens(self, sudachipy_tokens):
        if self.split_mode is None or self.split_mode == "A":  # do nothing for default split mode
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
                    sub_tokens_list.append([self._get_dtokens(sub_a, False), self._get_dtokens(sub_b, False)])
        return sub_tokens_list

    def _get_config(self):
        config = OrderedDict(
            (
                ("split_mode", self.split_mode),
            )
        )
        return config

    def _set_config(self, config={}):
        self.split_mode = config.get("split_mode", None)

    def to_bytes(self, **kwargs):
        serializers = OrderedDict(
            (
                ("cfg", lambda: srsly.json_dumps(self._get_config())),
            )
        )
        return util.to_bytes(serializers, [])

    def from_bytes(self, data, **kwargs):
        deserializers = OrderedDict(
            (
                ("cfg", lambda b: self._set_config(srsly.json_loads(b))),
            )
        )
        util.from_bytes(data, deserializers, [])
        self.tokenizer = try_sudachi_import(self.split_mode)
        return self

    def to_disk(self, path, **kwargs):
        path = util.ensure_path(path)
        serializers = OrderedDict(
            (
                ("cfg", lambda p: srsly.write_json(p, self._get_config())),
            )
        )
        return util.to_disk(path, serializers, [])

    def from_disk(self, path, **kwargs):
        path = util.ensure_path(path)
        serializers = OrderedDict(
            (
                ("cfg", lambda p: self._set_config(srsly.read_json(p))),
            )
        )
        util.from_disk(path, serializers, [])
        self.tokenizer = try_sudachi_import(self.split_mode)


class JapaneseDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters[LANG] = lambda _text: "ja"
    stop_words = STOP_WORDS
    tag_map = TAG_MAP
    syntax_iterators = SYNTAX_ITERATORS
    writing_system = {"direction": "ltr", "has_case": False, "has_letters": False}

    @classmethod
    def create_tokenizer(cls, nlp=None, config={}):
        return JapaneseTokenizer(cls, nlp, config)


class Japanese(Language):
    lang = "ja"
    Defaults = JapaneseDefaults

    def make_doc(self, text):
        return self.tokenizer(text)


def pickle_japanese(instance):
    return Japanese, tuple()


copy_reg.pickle(Japanese, pickle_japanese)

__all__ = ["Japanese"]

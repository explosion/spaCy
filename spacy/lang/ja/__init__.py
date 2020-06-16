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
DetailedToken = namedtuple("DetailedToken", ["surface", "pos", "lemma"])

# Handling for multiple spaces in a row is somewhat awkward, this simplifies
# the flow by creating a dummy with the same interface.
DummyNode = namedtuple("DummyNode", ["surface", "pos", "lemma"])
DummySpace = DummyNode(" ", " ", " ")


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


def resolve_pos(orth, pos, next_pos):
    """If necessary, add a field to the POS tag for UD mapping.
    Under Universal Dependencies, sometimes the same Unidic POS tag can
    be mapped differently depending on the literal token or its context
    in the sentence. This function returns resolved POSs for both token
    and next_token by tuple.
    """

    # Some tokens have their UD tag decided based on the POS of the following
    # token.

    # orth based rules
    if pos[0] in TAG_ORTH_MAP:
        orth_map = TAG_ORTH_MAP[pos[0]]
        if orth in orth_map:
            return orth_map[orth], None

    # tag bi-gram mapping
    if next_pos:
        tag_bigram = pos[0], next_pos[0]
        if tag_bigram in TAG_BIGRAM_MAP:
            bipos = TAG_BIGRAM_MAP[tag_bigram]
            if bipos[0] is None:
                return TAG_MAP[pos[0]][POS], bipos[1]
            else:
                return bipos

    return TAG_MAP[pos[0]][POS], None


# Use a mapping of paired punctuation to avoid splitting quoted sentences.
pairpunct = {'「':'」', '『': '』', '【': '】'}


def separate_sentences(doc):
    """Given a doc, mark tokens that start sentences based on Unidic tags.
    """

    stack = [] # save paired punctuation

    for i, token in enumerate(doc[:-2]):
        # Set all tokens after the first to false by default. This is necessary
        # for the doc code to be aware we've done sentencization, see
        # `is_sentenced`.
        token.sent_start = (i == 0)
        if token.tag_:
            if token.tag_ == "補助記号-括弧開":
                ts = str(token)
                if ts in pairpunct:
                    stack.append(pairpunct[ts])
                elif stack and ts == stack[-1]:
                    stack.pop()

            if token.tag_ == "補助記号-句点":
                next_token = doc[i+1]
                if next_token.tag_ != token.tag_ and not stack:
                    next_token.sent_start = True


def get_dtokens(tokenizer, text):
    tokens = tokenizer.tokenize(text)
    words = []
    for ti, token in enumerate(tokens):
        tag = '-'.join([xx for xx in token.part_of_speech()[:4] if xx != '*'])
        inf = '-'.join([xx for xx in token.part_of_speech()[4:] if xx != '*'])
        dtoken = DetailedToken(
                token.surface(),
                (tag, inf),
                token.dictionary_form())
        if ti > 0 and words[-1].pos[0] == '空白' and tag == '空白':
            # don't add multiple space tokens in a row
            continue
        words.append(dtoken)

    # remove empty tokens. These can be produced with characters like … that
    # Sudachi normalizes internally. 
    words = [ww for ww in words if len(ww.surface) > 0]
    return words


def get_words_lemmas_tags_spaces(dtokens, text, gap_tag=("空白", "")):
    words = [x.surface for x in dtokens]
    if "".join("".join(words).split()) != "".join(text.split()):
        raise ValueError(Errors.E194.format(text=text, words=words))
    text_words = []
    text_lemmas = []
    text_tags = []
    text_spaces = []
    text_pos = 0
    # handle empty and whitespace-only texts
    if len(words) == 0:
        return text_words, text_lemmas, text_tags, text_spaces
    elif len([word for word in words if not word.isspace()]) == 0:
        assert text.isspace()
        text_words = [text]
        text_lemmas = [text]
        text_tags = [gap_tag]
        text_spaces = [False]
        return text_words, text_lemmas, text_tags, text_spaces
    # normalize words to remove all whitespace tokens
    norm_words, norm_dtokens = zip(*[(word, dtokens) for word, dtokens in zip(words, dtokens) if not word.isspace()])
    # align words with text
    for word, dtoken in zip(norm_words, norm_dtokens):
        try:
            word_start = text[text_pos:].index(word)
        except ValueError:
            raise ValueError(Errors.E194.format(text=text, words=words))
        if word_start > 0:
            w = text[text_pos:text_pos + word_start]
            text_words.append(w)
            text_lemmas.append(w)
            text_tags.append(gap_tag)
            text_spaces.append(False)
            text_pos += word_start
        text_words.append(word)
        text_lemmas.append(dtoken.lemma)
        text_tags.append(dtoken.pos)
        text_spaces.append(False)
        text_pos += len(word)
        if text_pos < len(text) and text[text_pos] == " ":
            text_spaces[-1] = True
            text_pos += 1
    if text_pos < len(text):
        w = text[text_pos:]
        text_words.append(w)
        text_lemmas.append(w)
        text_tags.append(gap_tag)
        text_spaces.append(False)
    return text_words, text_lemmas, text_tags, text_spaces


class JapaneseTokenizer(DummyTokenizer):
    def __init__(self, cls, nlp=None, config={}):
        self.vocab = nlp.vocab if nlp is not None else cls.create_vocab(nlp)
        self.split_mode = config.get("split_mode", None)
        self.tokenizer = try_sudachi_import(self.split_mode)

    def __call__(self, text):
        dtokens = get_dtokens(self.tokenizer, text)

        words, lemmas, unidic_tags, spaces = get_words_lemmas_tags_spaces(dtokens, text)
        doc = Doc(self.vocab, words=words, spaces=spaces)
        next_pos = None
        for idx, (token, lemma, unidic_tag) in enumerate(zip(doc, lemmas, unidic_tags)):
            token.tag_ = unidic_tag[0]
            if next_pos:
                token.pos = next_pos
                next_pos = None
            else:
                token.pos, next_pos = resolve_pos(
                    token.orth_,
                    unidic_tag,
                    unidic_tags[idx + 1] if idx + 1 < len(unidic_tags) else None
                )

            # if there's no lemma info (it's an unk) just use the surface
            token.lemma_ = lemma
        doc.user_data["unidic_tags"] = unidic_tags

        return doc

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

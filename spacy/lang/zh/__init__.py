# coding: utf8
from __future__ import unicode_literals

import tempfile
import srsly
from pathlib import Path
from collections import OrderedDict
from ...attrs import LANG
from ...language import Language
from ...tokens import Doc
from ...util import DummyTokenizer
from ..tokenizer_exceptions import BASE_EXCEPTIONS
from .lex_attrs import LEX_ATTRS
from .stop_words import STOP_WORDS
from .tag_map import TAG_MAP
from ... import util


_PKUSEG_INSTALL_MSG = "install it with `pip install pkuseg==0.0.25` or from https://github.com/lancopku/pkuseg-python"


def try_jieba_import(use_jieba):
    try:
        import jieba

        # segment a short text to have jieba initialize its cache in advance
        list(jieba.cut("作为", cut_all=False))

        return jieba
    except ImportError:
        if use_jieba:
            msg = (
                "Jieba not installed. Either set the default to False with "
                "`from spacy.lang.zh import ChineseDefaults; ChineseDefaults.use_jieba = False`, "
                "or install it with `pip install jieba` or from "
                "https://github.com/fxsjy/jieba"
            )
            raise ImportError(msg)


def try_pkuseg_import(use_pkuseg, pkuseg_model, pkuseg_user_dict):
    try:
        import pkuseg

        if pkuseg_model:
            return pkuseg.pkuseg(pkuseg_model, pkuseg_user_dict)
        elif use_pkuseg:
            msg = (
                "Chinese.use_pkuseg is True but no pkuseg model was specified. "
                "Please provide the name of a pretrained model "
                "or the path to a model with "
                '`Chinese(meta={"tokenizer": {"config": {"pkuseg_model": name_or_path}}}).'
            )
            raise ValueError(msg)
    except ImportError:
        if use_pkuseg:
            msg = (
                "pkuseg not installed. Either set Chinese.use_pkuseg = False, "
                "or " + _PKUSEG_INSTALL_MSG
            )
            raise ImportError(msg)
    except FileNotFoundError:
        if use_pkuseg:
            msg = "Unable to load pkuseg model from: " + pkuseg_model
            raise FileNotFoundError(msg)


class ChineseTokenizer(DummyTokenizer):
    def __init__(self, cls, nlp=None, config={}):
        self.use_jieba = config.get("use_jieba", cls.use_jieba)
        self.use_pkuseg = config.get("use_pkuseg", cls.use_pkuseg)
        self.require_pkuseg = config.get("require_pkuseg", False)
        self.vocab = nlp.vocab if nlp is not None else cls.create_vocab(nlp)
        self.jieba_seg = try_jieba_import(self.use_jieba)
        self.pkuseg_seg = try_pkuseg_import(
            self.use_pkuseg,
            pkuseg_model=config.get("pkuseg_model", None),
            pkuseg_user_dict=config.get("pkuseg_user_dict", "default"),
        )
        # remove relevant settings from config so they're not also saved in
        # Language.meta
        for key in ["use_jieba", "use_pkuseg", "require_pkuseg", "pkuseg_model"]:
            if key in config:
                del config[key]
        self.tokenizer = Language.Defaults().create_tokenizer(nlp)

    def __call__(self, text):
        use_jieba = self.use_jieba
        use_pkuseg = self.use_pkuseg
        if self.require_pkuseg:
            use_jieba = False
            use_pkuseg = True
        if use_jieba:
            words = list([x for x in self.jieba_seg.cut(text, cut_all=False) if x])
            (words, spaces) = util.get_words_and_spaces(words, text)
            return Doc(self.vocab, words=words, spaces=spaces)
        elif use_pkuseg:
            words = self.pkuseg_seg.cut(text)
            (words, spaces) = util.get_words_and_spaces(words, text)
            return Doc(self.vocab, words=words, spaces=spaces)
        else:
            # split into individual characters
            words = list(text)
            (words, spaces) = util.get_words_and_spaces(words, text)
            return Doc(self.vocab, words=words, spaces=spaces)

    def pkuseg_update_user_dict(self, words, reset=False):
        if self.pkuseg_seg:
            if reset:
                try:
                    import pkuseg

                    self.pkuseg_seg.preprocesser = pkuseg.Preprocesser(None)
                except ImportError:
                    if self.use_pkuseg:
                        msg = (
                            "pkuseg not installed: unable to reset pkuseg "
                            "user dict. Please " + _PKUSEG_INSTALL_MSG
                        )
                        raise ImportError(msg)
            for word in words:
                self.pkuseg_seg.preprocesser.insert(word.strip(), "")

    def _get_config(self):
        config = OrderedDict(
            (
                ("use_jieba", self.use_jieba),
                ("use_pkuseg", self.use_pkuseg),
                ("require_pkuseg", self.require_pkuseg),
            )
        )
        return config

    def _set_config(self, config={}):
        self.use_jieba = config.get("use_jieba", False)
        self.use_pkuseg = config.get("use_pkuseg", False)
        self.require_pkuseg = config.get("require_pkuseg", False)

    def to_bytes(self, **kwargs):
        pkuseg_features_b = b""
        pkuseg_weights_b = b""
        pkuseg_processors_data = None
        if self.pkuseg_seg:
            with tempfile.TemporaryDirectory() as tempdir:
                self.pkuseg_seg.feature_extractor.save(tempdir)
                self.pkuseg_seg.model.save(tempdir)
                tempdir = Path(tempdir)
                with open(tempdir / "features.pkl", "rb") as fileh:
                    pkuseg_features_b = fileh.read()
                with open(tempdir / "weights.npz", "rb") as fileh:
                    pkuseg_weights_b = fileh.read()
            pkuseg_processors_data = (
                _get_pkuseg_trie_data(self.pkuseg_seg.preprocesser.trie),
                self.pkuseg_seg.postprocesser.do_process,
                sorted(list(self.pkuseg_seg.postprocesser.common_words)),
                sorted(list(self.pkuseg_seg.postprocesser.other_words)),
            )
        serializers = OrderedDict(
            (
                ("cfg", lambda: srsly.json_dumps(self._get_config())),
                ("pkuseg_features", lambda: pkuseg_features_b),
                ("pkuseg_weights", lambda: pkuseg_weights_b),
                (
                    "pkuseg_processors",
                    lambda: srsly.msgpack_dumps(pkuseg_processors_data),
                ),
            )
        )
        return util.to_bytes(serializers, [])

    def from_bytes(self, data, **kwargs):
        pkuseg_data = {"features_b": b"", "weights_b": b"", "processors_data": None}

        def deserialize_pkuseg_features(b):
            pkuseg_data["features_b"] = b

        def deserialize_pkuseg_weights(b):
            pkuseg_data["weights_b"] = b

        def deserialize_pkuseg_processors(b):
            pkuseg_data["processors_data"] = srsly.msgpack_loads(b)

        deserializers = OrderedDict(
            (
                ("cfg", lambda b: self._set_config(srsly.json_loads(b))),
                ("pkuseg_features", deserialize_pkuseg_features),
                ("pkuseg_weights", deserialize_pkuseg_weights),
                ("pkuseg_processors", deserialize_pkuseg_processors),
            )
        )
        util.from_bytes(data, deserializers, [])

        if pkuseg_data["features_b"] and pkuseg_data["weights_b"]:
            with tempfile.TemporaryDirectory() as tempdir:
                tempdir = Path(tempdir)
                with open(tempdir / "features.pkl", "wb") as fileh:
                    fileh.write(pkuseg_data["features_b"])
                with open(tempdir / "weights.npz", "wb") as fileh:
                    fileh.write(pkuseg_data["weights_b"])
                try:
                    import pkuseg
                except ImportError:
                    raise ImportError(
                        "pkuseg not installed. To use this model, "
                        + _PKUSEG_INSTALL_MSG
                    )
                self.pkuseg_seg = pkuseg.pkuseg(str(tempdir))
            if pkuseg_data["processors_data"]:
                processors_data = pkuseg_data["processors_data"]
                (user_dict, do_process, common_words, other_words) = processors_data
                self.pkuseg_seg.preprocesser = pkuseg.Preprocesser(user_dict)
                self.pkuseg_seg.postprocesser.do_process = do_process
                self.pkuseg_seg.postprocesser.common_words = set(common_words)
                self.pkuseg_seg.postprocesser.other_words = set(other_words)

        return self

    def to_disk(self, path, **kwargs):
        path = util.ensure_path(path)

        def save_pkuseg_model(path):
            if self.pkuseg_seg:
                if not path.exists():
                    path.mkdir(parents=True)
                self.pkuseg_seg.model.save(path)
                self.pkuseg_seg.feature_extractor.save(path)

        def save_pkuseg_processors(path):
            if self.pkuseg_seg:
                data = (
                    _get_pkuseg_trie_data(self.pkuseg_seg.preprocesser.trie),
                    self.pkuseg_seg.postprocesser.do_process,
                    sorted(list(self.pkuseg_seg.postprocesser.common_words)),
                    sorted(list(self.pkuseg_seg.postprocesser.other_words)),
                )
                srsly.write_msgpack(path, data)

        serializers = OrderedDict(
            (
                ("cfg", lambda p: srsly.write_json(p, self._get_config())),
                ("pkuseg_model", lambda p: save_pkuseg_model(p)),
                ("pkuseg_processors", lambda p: save_pkuseg_processors(p)),
            )
        )
        return util.to_disk(path, serializers, [])

    def from_disk(self, path, **kwargs):
        path = util.ensure_path(path)

        def load_pkuseg_model(path):
            try:
                import pkuseg
            except ImportError:
                if self.use_pkuseg:
                    raise ImportError(
                        "pkuseg not installed. To use this model, "
                        + _PKUSEG_INSTALL_MSG
                    )
            if path.exists():
                self.pkuseg_seg = pkuseg.pkuseg(path)

        def load_pkuseg_processors(path):
            try:
                import pkuseg
            except ImportError:
                if self.use_pkuseg:
                    raise ImportError(self._pkuseg_install_msg)
            if self.pkuseg_seg:
                data = srsly.read_msgpack(path)
                (user_dict, do_process, common_words, other_words) = data
                self.pkuseg_seg.preprocesser = pkuseg.Preprocesser(user_dict)
                self.pkuseg_seg.postprocesser.do_process = do_process
                self.pkuseg_seg.postprocesser.common_words = set(common_words)
                self.pkuseg_seg.postprocesser.other_words = set(other_words)

        serializers = OrderedDict(
            (
                ("cfg", lambda p: self._set_config(srsly.read_json(p))),
                ("pkuseg_model", lambda p: load_pkuseg_model(p)),
                ("pkuseg_processors", lambda p: load_pkuseg_processors(p)),
            )
        )
        util.from_disk(path, serializers, [])


class ChineseDefaults(Language.Defaults):
    lex_attr_getters = dict(Language.Defaults.lex_attr_getters)
    lex_attr_getters.update(LEX_ATTRS)
    lex_attr_getters[LANG] = lambda text: "zh"
    tokenizer_exceptions = BASE_EXCEPTIONS
    stop_words = STOP_WORDS
    tag_map = TAG_MAP
    writing_system = {"direction": "ltr", "has_case": False, "has_letters": False}
    use_jieba = True
    use_pkuseg = False

    @classmethod
    def create_tokenizer(cls, nlp=None, config={}):
        return ChineseTokenizer(cls, nlp, config=config)


class Chinese(Language):
    lang = "zh"
    Defaults = ChineseDefaults  # override defaults

    def make_doc(self, text):
        return self.tokenizer(text)


def _get_pkuseg_trie_data(node, path=""):
    data = []
    for c, child_node in sorted(node.children.items()):
        data.extend(_get_pkuseg_trie_data(child_node, path + c))
    if node.isword:
        data.append((path, node.usertag))
    return data


__all__ = ["Chinese"]

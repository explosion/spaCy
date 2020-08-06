from typing import Optional, List, Dict, Any
from enum import Enum
import tempfile
import srsly
import warnings
from pathlib import Path
from thinc.api import Config

from ...errors import Warnings, Errors
from ...language import Language
from ...tokens import Doc
from ...util import DummyTokenizer, registry
from .lex_attrs import LEX_ATTRS
from .stop_words import STOP_WORDS
from ... import util


_PKUSEG_INSTALL_MSG = "install it with `pip install pkuseg==0.0.25` or from https://github.com/lancopku/pkuseg-python"

DEFAULT_CONFIG = """
[nlp]

[nlp.tokenizer]
@tokenizers = "spacy.zh.ChineseTokenizer"
segmenter = "char"
pkuseg_model = null
pkuseg_user_dict = "default"
"""


class Segmenter(str, Enum):
    char = "char"
    jieba = "jieba"
    pkuseg = "pkuseg"

    @classmethod
    def values(cls):
        return list(cls.__members__.keys())


@registry.tokenizers("spacy.zh.ChineseTokenizer")
def create_chinese_tokenizer(
    segmenter: Segmenter = Segmenter.char,
    pkuseg_model: Optional[str] = None,
    pkuseg_user_dict: Optional[str] = "default",
):
    def chinese_tokenizer_factory(nlp):
        return ChineseTokenizer(
            nlp,
            segmenter=segmenter,
            pkuseg_model=pkuseg_model,
            pkuseg_user_dict=pkuseg_user_dict,
        )

    return chinese_tokenizer_factory


class ChineseTokenizer(DummyTokenizer):
    def __init__(
        self,
        nlp: Language,
        segmenter: Segmenter = Segmenter.char,
        pkuseg_model: Optional[str] = None,
        pkuseg_user_dict: Optional[str] = None,
    ):
        self.vocab = nlp.vocab
        if isinstance(segmenter, Segmenter):  # we might have the Enum here
            segmenter = segmenter.value
        self.segmenter = segmenter
        self.pkuseg_model = pkuseg_model
        self.pkuseg_user_dict = pkuseg_user_dict
        self.pkuseg_seg = None
        self.jieba_seg = None
        self.configure_segmenter(segmenter)

    def configure_segmenter(self, segmenter: str):
        if segmenter not in Segmenter.values():
            warn_msg = Warnings.W103.format(
                lang="Chinese",
                segmenter=segmenter,
                supported=", ".join(Segmenter.values()),
                default="'char' (character segmentation)",
            )
            warnings.warn(warn_msg)
            self.segmenter = Segmenter.char
        self.jieba_seg = try_jieba_import(self.segmenter)
        self.pkuseg_seg = try_pkuseg_import(
            self.segmenter,
            pkuseg_model=self.pkuseg_model,
            pkuseg_user_dict=self.pkuseg_user_dict,
        )

    def __call__(self, text: str) -> Doc:
        if self.segmenter == Segmenter.jieba:
            words = list([x for x in self.jieba_seg.cut(text, cut_all=False) if x])
            (words, spaces) = util.get_words_and_spaces(words, text)
            return Doc(self.vocab, words=words, spaces=spaces)
        elif self.segmenter == Segmenter.pkuseg:
            if self.pkuseg_seg is None:
                raise ValueError(Errors.E1000)
            words = self.pkuseg_seg.cut(text)
            (words, spaces) = util.get_words_and_spaces(words, text)
            return Doc(self.vocab, words=words, spaces=spaces)

        # warn if segmenter setting is not the only remaining option "char"
        if self.segmenter != Segmenter.char:
            warn_msg = Warnings.W103.format(
                lang="Chinese",
                segmenter=self.segmenter,
                supported=", ".join(Segmenter.values()),
                default="'char' (character segmentation)",
            )
            warnings.warn(warn_msg)

        # split into individual characters
        words = list(text)
        (words, spaces) = util.get_words_and_spaces(words, text)
        return Doc(self.vocab, words=words, spaces=spaces)

    def pkuseg_update_user_dict(self, words: List[str], reset: bool = False):
        if self.segmenter == Segmenter.pkuseg:
            if reset:
                try:
                    import pkuseg

                    self.pkuseg_seg.preprocesser = pkuseg.Preprocesser(None)
                except ImportError:
                    msg = (
                        "pkuseg not installed: unable to reset pkuseg "
                        "user dict. Please " + _PKUSEG_INSTALL_MSG
                    )
                    raise ImportError(msg) from None
            for word in words:
                self.pkuseg_seg.preprocesser.insert(word.strip(), "")
        else:
            warn_msg = Warnings.W104.format(target="pkuseg", current=self.segmenter)
            warnings.warn(warn_msg)

    def _get_config(self) -> Dict[str, Any]:
        return {
            "segmenter": self.segmenter,
            "pkuseg_model": self.pkuseg_model,
            "pkuseg_user_dict": self.pkuseg_user_dict,
        }

    def _set_config(self, config: Dict[str, Any] = {}) -> None:
        self.segmenter = config.get("segmenter", Segmenter.char)
        self.pkuseg_model = config.get("pkuseg_model", None)
        self.pkuseg_user_dict = config.get("pkuseg_user_dict", "default")

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
        serializers = {
            "cfg": lambda: srsly.json_dumps(self._get_config()),
            "pkuseg_features": lambda: pkuseg_features_b,
            "pkuseg_weights": lambda: pkuseg_weights_b,
            "pkuseg_processors": lambda: srsly.msgpack_dumps(pkuseg_processors_data),
        }
        return util.to_bytes(serializers, [])

    def from_bytes(self, data, **kwargs):
        pkuseg_data = {"features_b": b"", "weights_b": b"", "processors_data": None}

        def deserialize_pkuseg_features(b):
            pkuseg_data["features_b"] = b

        def deserialize_pkuseg_weights(b):
            pkuseg_data["weights_b"] = b

        def deserialize_pkuseg_processors(b):
            pkuseg_data["processors_data"] = srsly.msgpack_loads(b)

        deserializers = {
            "cfg": lambda b: self._set_config(srsly.json_loads(b)),
            "pkuseg_features": deserialize_pkuseg_features,
            "pkuseg_weights": deserialize_pkuseg_weights,
            "pkuseg_processors": deserialize_pkuseg_processors,
        }
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
                    ) from None
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

        serializers = {
            "cfg": lambda p: srsly.write_json(p, self._get_config()),
            "pkuseg_model": lambda p: save_pkuseg_model(p),
            "pkuseg_processors": lambda p: save_pkuseg_processors(p),
        }
        return util.to_disk(path, serializers, [])

    def from_disk(self, path, **kwargs):
        path = util.ensure_path(path)

        def load_pkuseg_model(path):
            try:
                import pkuseg
            except ImportError:
                if self.segmenter == Segmenter.pkuseg:
                    raise ImportError(
                        "pkuseg not installed. To use this model, "
                        + _PKUSEG_INSTALL_MSG
                    ) from None
            if path.exists():
                self.pkuseg_seg = pkuseg.pkuseg(path)

        def load_pkuseg_processors(path):
            try:
                import pkuseg
            except ImportError:
                if self.segmenter == Segmenter.pkuseg:
                    raise ImportError(self._pkuseg_install_msg) from None
            if self.segmenter == Segmenter.pkuseg:
                data = srsly.read_msgpack(path)
                (user_dict, do_process, common_words, other_words) = data
                self.pkuseg_seg.preprocesser = pkuseg.Preprocesser(user_dict)
                self.pkuseg_seg.postprocesser.do_process = do_process
                self.pkuseg_seg.postprocesser.common_words = set(common_words)
                self.pkuseg_seg.postprocesser.other_words = set(other_words)

        serializers = {
            "cfg": lambda p: self._set_config(srsly.read_json(p)),
            "pkuseg_model": lambda p: load_pkuseg_model(p),
            "pkuseg_processors": lambda p: load_pkuseg_processors(p),
        }
        util.from_disk(path, serializers, [])


class ChineseDefaults(Language.Defaults):
    config = Config().from_str(DEFAULT_CONFIG)
    lex_attr_getters = LEX_ATTRS
    stop_words = STOP_WORDS
    writing_system = {"direction": "ltr", "has_case": False, "has_letters": False}


class Chinese(Language):
    lang = "zh"
    Defaults = ChineseDefaults


def try_jieba_import(segmenter: str) -> None:
    try:
        import jieba

        if segmenter == Segmenter.jieba:
            # segment a short text to have jieba initialize its cache in advance
            list(jieba.cut("作为", cut_all=False))

        return jieba
    except ImportError:
        if segmenter == Segmenter.jieba:
            msg = (
                "Jieba not installed. To use jieba, install it with `pip "
                " install jieba` or from https://github.com/fxsjy/jieba"
            )
            raise ImportError(msg) from None


def try_pkuseg_import(segmenter: str, pkuseg_model: str, pkuseg_user_dict: str) -> None:
    try:
        import pkuseg

        if pkuseg_model:
            return pkuseg.pkuseg(pkuseg_model, pkuseg_user_dict)
        elif segmenter == Segmenter.pkuseg:
            msg = (
                "The Chinese word segmenter is 'pkuseg' but no pkuseg model "
                "was specified. Please provide the name of a pretrained model "
                "or the path to a model with:\n"
                'cfg = {"nlp": {"tokenizer": {"segmenter": "pkuseg", "pkuseg_model": name_or_path }}\n'
                "nlp = Chinese.from_config(cfg)"
            )
            raise ValueError(msg)
    except ImportError:
        if segmenter == Segmenter.pkuseg:
            msg = "pkuseg not installed. To use pkuseg, " + _PKUSEG_INSTALL_MSG
            raise ImportError(msg) from None
    except FileNotFoundError:
        if segmenter == Segmenter.pkuseg:
            msg = "Unable to load pkuseg model from: " + pkuseg_model
            raise FileNotFoundError(msg) from None


def _get_pkuseg_trie_data(node, path=""):
    data = []
    for c, child_node in sorted(node.children.items()):
        data.extend(_get_pkuseg_trie_data(child_node, path + c))
    if node.isword:
        data.append((path, node.usertag))
    return data


__all__ = ["Chinese"]

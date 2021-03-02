from typing import Dict, Any
import srsly

from ..language import Language
from ..matcher import Matcher
from ..tokens import Doc
from .. import util


@Language.component(
    "merge_noun_chunks",
    requires=["token.dep", "token.tag", "token.pos"],
    retokenizes=True,
)
def merge_noun_chunks(doc: Doc) -> Doc:
    """Merge noun chunks into a single token.

    doc (Doc): The Doc object.
    RETURNS (Doc): The Doc object with merged noun chunks.

    DOCS: https://spacy.io/api/pipeline-functions#merge_noun_chunks
    """
    if not doc.has_annotation("DEP"):
        return doc
    with doc.retokenize() as retokenizer:
        for np in doc.noun_chunks:
            attrs = {"tag": np.root.tag, "dep": np.root.dep}
            retokenizer.merge(np, attrs=attrs)
    return doc


@Language.component(
    "merge_entities",
    requires=["doc.ents", "token.ent_iob", "token.ent_type"],
    retokenizes=True,
)
def merge_entities(doc: Doc):
    """Merge entities into a single token.

    doc (Doc): The Doc object.
    RETURNS (Doc): The Doc object with merged entities.

    DOCS: https://spacy.io/api/pipeline-functions#merge_entities
    """
    with doc.retokenize() as retokenizer:
        for ent in doc.ents:
            attrs = {"tag": ent.root.tag, "dep": ent.root.dep, "ent_type": ent.label}
            retokenizer.merge(ent, attrs=attrs)
    return doc


@Language.component("merge_subtokens", requires=["token.dep"], retokenizes=True)
def merge_subtokens(doc: Doc, label: str = "subtok") -> Doc:
    """Merge subtokens into a single token.

    doc (Doc): The Doc object.
    label (str): The subtoken dependency label.
    RETURNS (Doc): The Doc object with merged subtokens.

    DOCS: https://spacy.io/api/pipeline-functions#merge_subtokens
    """
    # TODO: make stateful component with "label" config
    merger = Matcher(doc.vocab)
    merger.add("SUBTOK", [[{"DEP": label, "op": "+"}]])
    matches = merger(doc)
    spans = util.filter_spans([doc[start : end + 1] for _, start, end in matches])
    with doc.retokenize() as retokenizer:
        for span in spans:
            retokenizer.merge(span)
    return doc


@Language.factory(
    "token_splitter",
    default_config={"min_length": 25, "split_length": 10},
    retokenizes=True,
)
def make_token_splitter(
    nlp: Language, name: str, *, min_length: int = 0, split_length: int = 0
):
    return TokenSplitter(min_length=min_length, split_length=split_length)


class TokenSplitter:
    def __init__(self, min_length: int = 0, split_length: int = 0):
        self.min_length = min_length
        self.split_length = split_length

    def __call__(self, doc: Doc) -> Doc:
        if self.min_length > 0 and self.split_length > 0:
            with doc.retokenize() as retokenizer:
                for t in doc:
                    if len(t.text) >= self.min_length:
                        orths = []
                        heads = []
                        attrs = {}
                        for i in range(0, len(t.text), self.split_length):
                            orths.append(t.text[i : i + self.split_length])
                            heads.append((t, i / self.split_length))
                        retokenizer.split(t, orths, heads, attrs)
        return doc

    def _get_config(self) -> Dict[str, Any]:
        return {
            "min_length": self.min_length,
            "split_length": self.split_length,
        }

    def _set_config(self, config: Dict[str, Any] = {}) -> None:
        self.min_length = config.get("min_length", 0)
        self.split_length = config.get("split_length", 0)

    def to_bytes(self, **kwargs):
        serializers = {
            "cfg": lambda: srsly.json_dumps(self._get_config()),
        }
        return util.to_bytes(serializers, [])

    def from_bytes(self, data, **kwargs):
        deserializers = {
            "cfg": lambda b: self._set_config(srsly.json_loads(b)),
        }
        util.from_bytes(data, deserializers, [])
        return self

    def to_disk(self, path, **kwargs):
        path = util.ensure_path(path)
        serializers = {
            "cfg": lambda p: srsly.write_json(p, self._get_config()),
        }
        return util.to_disk(path, serializers, [])

    def from_disk(self, path, **kwargs):
        path = util.ensure_path(path)
        serializers = {
            "cfg": lambda p: self._set_config(srsly.read_json(p)),
        }
        util.from_disk(path, serializers, [])

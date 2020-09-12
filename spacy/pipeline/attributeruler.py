import srsly
from typing import List, Dict, Union, Iterable, Any, Optional
from pathlib import Path

from .pipe import Pipe
from ..errors import Errors
from ..training import validate_examples
from ..language import Language
from ..matcher import Matcher
from ..scorer import Scorer
from ..symbols import IDS, TAG, POS, MORPH, LEMMA
from ..tokens import Doc, Span
from ..tokens._retokenize import normalize_token_attrs, set_token_attrs
from ..vocab import Vocab
from ..util import SimpleFrozenList
from .. import util


MatcherPatternType = List[Dict[Union[int, str], Any]]
AttributeRulerPatternType = Dict[str, Union[MatcherPatternType, Dict, int]]


@Language.factory(
    "attribute_ruler", default_config={"pattern_dicts": None, "validate": False}
)
def make_attribute_ruler(
    nlp: Language,
    name: str,
    pattern_dicts: Optional[Iterable[AttributeRulerPatternType]],
    validate: bool,
):
    return AttributeRuler(
        nlp.vocab, name, pattern_dicts=pattern_dicts, validate=validate
    )


class AttributeRuler(Pipe):
    """Set token-level attributes for tokens matched by Matcher patterns.
    Additionally supports importing patterns from tag maps and morph rules.

    DOCS: https://nightly.spacy.io/api/attributeruler
    """

    def __init__(
        self,
        vocab: Vocab,
        name: str = "attribute_ruler",
        *,
        pattern_dicts: Optional[Iterable[AttributeRulerPatternType]] = None,
        validate: bool = False,
    ) -> None:
        """Initialize the AttributeRuler.

        vocab (Vocab): The vocab.
        name (str): The pipe name. Defaults to "attribute_ruler".
        pattern_dicts (Iterable[Dict]): A list of pattern dicts with the keys as
        the arguments to AttributeRuler.add (`patterns`/`attrs`/`index`) to add
        as patterns.

        RETURNS (AttributeRuler): The AttributeRuler component.

        DOCS: https://nightly.spacy.io/api/attributeruler#init
        """
        self.name = name
        self.vocab = vocab
        self.matcher = Matcher(self.vocab, validate=validate)
        self.attrs = []
        self._attrs_unnormed = []  # store for reference
        self.indices = []

        if pattern_dicts:
            self.add_patterns(pattern_dicts)

    def __call__(self, doc: Doc) -> Doc:
        """Apply the AttributeRuler to a Doc and set all attribute exceptions.

        doc (Doc): The document to process.
        RETURNS (Doc): The processed Doc.

        DOCS: https://nightly.spacy.io/api/attributeruler#call
        """
        matches = sorted(self.matcher(doc))

        for match_id, start, end in matches:
            span = Span(doc, start, end, label=match_id)
            attrs = self.attrs[span.label]
            index = self.indices[span.label]
            try:
                token = span[index]
            except IndexError:
                raise ValueError(
                    Errors.E1001.format(
                        patterns=self.matcher.get(span.label),
                        span=[t.text for t in span],
                        index=index,
                    )
                ) from None
            set_token_attrs(token, attrs)
        return doc

    def pipe(self, stream, *, batch_size=128):
        """Apply the pipe to a stream of documents. This usually happens under
        the hood when the nlp object is called on a text and all components are
        applied to the Doc.

        stream (Iterable[Doc]): A stream of documents.
        batch_size (int): The number of documents to buffer.
        YIELDS (Doc): Processed documents in order.

        DOCS: https://spacy.io/attributeruler/pipe#pipe
        """
        for doc in stream:
            doc = self(doc)
            yield doc

    def load_from_tag_map(
        self, tag_map: Dict[str, Dict[Union[int, str], Union[int, str]]]
    ) -> None:
        """Load attribute ruler patterns from a tag map.

        tag_map (dict): The tag map that maps fine-grained tags to
            coarse-grained tags and morphological features.

        DOCS: https://nightly.spacy.io/api/attributeruler#load_from_morph_rules
        """
        for tag, attrs in tag_map.items():
            pattern = [{"TAG": tag}]
            attrs, morph_attrs = _split_morph_attrs(attrs)
            morph = self.vocab.morphology.add(morph_attrs)
            attrs["MORPH"] = self.vocab.strings[morph]
            self.add([pattern], attrs)

    def load_from_morph_rules(
        self, morph_rules: Dict[str, Dict[str, Dict[Union[int, str], Union[int, str]]]]
    ) -> None:
        """Load attribute ruler patterns from morph rules.

        morph_rules (dict): The morph rules that map token text and
            fine-grained tags to coarse-grained tags, lemmas and morphological
            features.

        DOCS: https://nightly.spacy.io/api/attributeruler#load_from_morph_rules
        """
        for tag in morph_rules:
            for word in morph_rules[tag]:
                pattern = [{"ORTH": word, "TAG": tag}]
                attrs = morph_rules[tag][word]
                attrs, morph_attrs = _split_morph_attrs(attrs)
                morph = self.vocab.morphology.add(morph_attrs)
                attrs["MORPH"] = self.vocab.strings[morph]
                self.add([pattern], attrs)

    def add(
        self, patterns: Iterable[MatcherPatternType], attrs: Dict, index: int = 0
    ) -> None:
        """Add Matcher patterns for tokens that should be modified with the
        provided attributes. The token at the specified index within the
        matched span will be assigned the attributes.

        patterns (Iterable[List[Dict]]): A list of Matcher patterns.
        attrs (Dict): The attributes to assign to the target token in the
            matched span.
        index (int): The index of the token in the matched span to modify. May
            be negative to index from the end of the span. Defaults to 0.

        DOCS: https://nightly.spacy.io/api/attributeruler#add
        """
        self.matcher.add(len(self.attrs), patterns)
        self._attrs_unnormed.append(attrs)
        attrs = normalize_token_attrs(self.vocab, attrs)
        self.attrs.append(attrs)
        self.indices.append(index)

    def add_patterns(self, pattern_dicts: Iterable[AttributeRulerPatternType]) -> None:
        """Add patterns from a list of pattern dicts with the keys as the
        arguments to AttributeRuler.add.
        pattern_dicts (Iterable[dict]): A list of pattern dicts with the keys
            as the arguments to AttributeRuler.add (patterns/attrs/index) to
            add as patterns.

        DOCS: https://nightly.spacy.io/api/attributeruler#add_patterns
        """
        for p in pattern_dicts:
            self.add(**p)

    @property
    def patterns(self) -> List[AttributeRulerPatternType]:
        """All the added patterns."""
        all_patterns = []
        for i in range(len(self.attrs)):
            p = {}
            p["patterns"] = self.matcher.get(i)[1]
            p["attrs"] = self._attrs_unnormed[i]
            p["index"] = self.indices[i]
            all_patterns.append(p)
        return all_patterns

    def score(self, examples, **kwargs):
        """Score a batch of examples.

        examples (Iterable[Example]): The examples to score.
        RETURNS (Dict[str, Any]): The scores, produced by
            Scorer.score_token_attr for the attributes "tag", "pos", "morph"
            and "lemma" for the target token attributes.

        DOCS: https://nightly.spacy.io/api/tagger#score
        """
        validate_examples(examples, "AttributeRuler.score")
        results = {}
        attrs = set()
        for token_attrs in self.attrs:
            attrs.update(token_attrs)
        for attr in attrs:
            if attr == TAG:
                results.update(Scorer.score_token_attr(examples, "tag", **kwargs))
            elif attr == POS:
                results.update(Scorer.score_token_attr(examples, "pos", **kwargs))
            elif attr == MORPH:
                results.update(Scorer.score_token_attr(examples, "morph", **kwargs))
            elif attr == LEMMA:
                results.update(Scorer.score_token_attr(examples, "lemma", **kwargs))
        return results

    def to_bytes(self, exclude: Iterable[str] = SimpleFrozenList()) -> bytes:
        """Serialize the AttributeRuler to a bytestring.

        exclude (Iterable[str]): String names of serialization fields to exclude.
        RETURNS (bytes): The serialized object.

        DOCS: https://nightly.spacy.io/api/attributeruler#to_bytes
        """
        serialize = {}
        serialize["vocab"] = self.vocab.to_bytes
        serialize["patterns"] = lambda: srsly.msgpack_dumps(self.patterns)
        return util.to_bytes(serialize, exclude)

    def from_bytes(
        self, bytes_data: bytes, exclude: Iterable[str] = SimpleFrozenList()
    ):
        """Load the AttributeRuler from a bytestring.

        bytes_data (bytes): The data to load.
        exclude (Iterable[str]): String names of serialization fields to exclude.
        returns (AttributeRuler): The loaded object.

        DOCS: https://nightly.spacy.io/api/attributeruler#from_bytes
        """

        def load_patterns(b):
            self.add_patterns(srsly.msgpack_loads(b))

        deserialize = {
            "vocab": lambda b: self.vocab.from_bytes(b),
            "patterns": load_patterns,
        }
        util.from_bytes(bytes_data, deserialize, exclude)

        return self

    def to_disk(
        self, path: Union[Path, str], exclude: Iterable[str] = SimpleFrozenList()
    ) -> None:
        """Serialize the AttributeRuler to disk.

        path (Union[Path, str]): A path to a directory.
        exclude (Iterable[str]): String names of serialization fields to exclude.
        DOCS: https://nightly.spacy.io/api/attributeruler#to_disk
        """
        serialize = {
            "vocab": lambda p: self.vocab.to_disk(p),
            "patterns": lambda p: srsly.write_msgpack(p, self.patterns),
        }
        util.to_disk(path, serialize, exclude)

    def from_disk(
        self, path: Union[Path, str], exclude: Iterable[str] = SimpleFrozenList()
    ) -> None:
        """Load the AttributeRuler from disk.

        path (Union[Path, str]): A path to a directory.
        exclude (Iterable[str]): String names of serialization fields to exclude.
        DOCS: https://nightly.spacy.io/api/attributeruler#from_disk
        """

        def load_patterns(p):
            self.add_patterns(srsly.read_msgpack(p))

        deserialize = {
            "vocab": lambda p: self.vocab.from_disk(p),
            "patterns": load_patterns,
        }
        util.from_disk(path, deserialize, exclude)

        return self


def _split_morph_attrs(attrs):
    """Split entries from a tag map or morph rules dict into to two dicts, one
    with the token-level features (POS, LEMMA) and one with the remaining
    features, which are presumed to be individual MORPH features."""
    other_attrs = {}
    morph_attrs = {}
    for k, v in attrs.items():
        if k in "_" or k in IDS.keys() or k in IDS.values():
            other_attrs[k] = v
        else:
            morph_attrs[k] = v
    return other_attrs, morph_attrs

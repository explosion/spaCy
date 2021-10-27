from typing import List, Dict, Union, Iterable, Any, Optional, Callable
from typing import Tuple
import srsly
from pathlib import Path

from .pipe import Pipe
from ..errors import Errors
from ..training import Example
from ..language import Language
from ..matcher import Matcher
from ..scorer import Scorer
from ..symbols import IDS
from ..tokens import Doc, Span
from ..tokens._retokenize import normalize_token_attrs, set_token_attrs
from ..vocab import Vocab
from ..util import SimpleFrozenList, registry
from .. import util


MatcherPatternType = List[Dict[Union[int, str], Any]]
AttributeRulerPatternType = Dict[str, Union[MatcherPatternType, Dict, int]]
TagMapType = Dict[str, Dict[Union[int, str], Union[int, str]]]
MorphRulesType = Dict[str, Dict[str, Dict[Union[int, str], Union[int, str]]]]


@Language.factory(
    "attribute_ruler",
    default_config={
        "validate": False,
        "scorer": {"@scorers": "spacy.attribute_ruler_scorer.v1"},
    },
)
def make_attribute_ruler(
    nlp: Language, name: str, validate: bool, scorer: Optional[Callable]
):
    return AttributeRuler(nlp.vocab, name, validate=validate, scorer=scorer)


def attribute_ruler_score(examples: Iterable[Example], **kwargs) -> Dict[str, Any]:
    def morph_key_getter(token, attr):
        return getattr(token, attr).key

    results = {}
    results.update(Scorer.score_token_attr(examples, "tag", **kwargs))
    results.update(Scorer.score_token_attr(examples, "pos", **kwargs))
    results.update(
        Scorer.score_token_attr(examples, "morph", getter=morph_key_getter, **kwargs)
    )
    results.update(
        Scorer.score_token_attr_per_feat(
            examples, "morph", getter=morph_key_getter, **kwargs
        )
    )
    results.update(Scorer.score_token_attr(examples, "lemma", **kwargs))
    return results


@registry.scorers("spacy.attribute_ruler_scorer.v1")
def make_attribute_ruler_scorer():
    return attribute_ruler_score


class AttributeRuler(Pipe):
    """Set token-level attributes for tokens matched by Matcher patterns.
    Additionally supports importing patterns from tag maps and morph rules.

    DOCS: https://spacy.io/api/attributeruler
    """

    def __init__(
        self,
        vocab: Vocab,
        name: str = "attribute_ruler",
        *,
        validate: bool = False,
        scorer: Optional[Callable] = attribute_ruler_score,
    ) -> None:
        """Create the AttributeRuler. After creation, you can add patterns
        with the `.initialize()` or `.add_patterns()` methods, or load patterns
        with `.from_bytes()` or `.from_disk()`. Loading patterns will remove
        any patterns you've added previously.

        vocab (Vocab): The vocab.
        name (str): The pipe name. Defaults to "attribute_ruler".
        scorer (Optional[Callable]): The scoring method. Defaults to
            Scorer.score_token_attr for the attributes "tag", "pos", "morph" and
            "lemma" and Scorer.score_token_attr_per_feat for the attribute
            "morph".

        RETURNS (AttributeRuler): The AttributeRuler component.

        DOCS: https://spacy.io/api/attributeruler#init
        """
        self.name = name
        self.vocab = vocab
        self.matcher = Matcher(self.vocab, validate=validate)
        self.validate = validate
        self.attrs: List[Dict] = []
        self._attrs_unnormed: List[Dict] = []  # store for reference
        self.indices: List[int] = []
        self.scorer = scorer

    def clear(self) -> None:
        """Reset all patterns."""
        self.matcher = Matcher(self.vocab, validate=self.validate)
        self.attrs = []
        self._attrs_unnormed = []
        self.indices = []

    def initialize(
        self,
        get_examples: Optional[Callable[[], Iterable[Example]]],
        *,
        nlp: Optional[Language] = None,
        patterns: Optional[Iterable[AttributeRulerPatternType]] = None,
        tag_map: Optional[TagMapType] = None,
        morph_rules: Optional[MorphRulesType] = None,
    ) -> None:
        """Initialize the attribute ruler by adding zero or more patterns.

        Rules can be specified as a sequence of dicts using the `patterns`
        keyword argument. You can also provide rules using the "tag map" or
        "morph rules" formats supported by spaCy prior to v3.
        """
        self.clear()
        if patterns:
            self.add_patterns(patterns)
        if tag_map:
            self.load_from_tag_map(tag_map)
        if morph_rules:
            self.load_from_morph_rules(morph_rules)

    def __call__(self, doc: Doc) -> Doc:
        """Apply the AttributeRuler to a Doc and set all attribute exceptions.

        doc (Doc): The document to process.
        RETURNS (Doc): The processed Doc.

        DOCS: https://spacy.io/api/attributeruler#call
        """
        error_handler = self.get_error_handler()
        try:
            matches = self.match(doc)
            self.set_annotations(doc, matches)
            return doc
        except Exception as e:
            return error_handler(self.name, self, [doc], e)

    def match(self, doc: Doc):
        matches = self.matcher(doc, allow_missing=True, as_spans=False)
        # Sort by the attribute ID, so that later rules have precedence
        matches = [
            (int(self.vocab.strings[m_id]), m_id, s, e) for m_id, s, e in matches  # type: ignore
        ]
        matches.sort()
        return matches

    def set_annotations(self, doc, matches):
        """Modify the document in place"""
        for attr_id, match_id, start, end in matches:
            span = Span(doc, start, end, label=match_id)
            attrs = self.attrs[attr_id]
            index = self.indices[attr_id]
            try:
                # The index can be negative, which makes it annoying to do
                # the boundscheck. Let Span do it instead.
                token = span[index]  # noqa: F841
            except IndexError:
                # The original exception is just our conditional logic, so we
                # raise from.
                raise ValueError(
                    Errors.E1001.format(
                        patterns=self.matcher.get(span.label),
                        span=[t.text for t in span],
                        index=index,
                    )
                ) from None
            set_token_attrs(span[index], attrs)

    def load_from_tag_map(
        self, tag_map: Dict[str, Dict[Union[int, str], Union[int, str]]]
    ) -> None:
        """Load attribute ruler patterns from a tag map.

        tag_map (dict): The tag map that maps fine-grained tags to
            coarse-grained tags and morphological features.

        DOCS: https://spacy.io/api/attributeruler#load_from_morph_rules
        """
        for tag, attrs in tag_map.items():
            pattern = [{"TAG": tag}]
            attrs, morph_attrs = _split_morph_attrs(attrs)
            if "MORPH" not in attrs:
                morph = self.vocab.morphology.add(morph_attrs)
                attrs["MORPH"] = self.vocab.strings[morph]
            else:
                morph = self.vocab.morphology.add(attrs["MORPH"])
                attrs["MORPH"] = self.vocab.strings[morph]
            self.add([pattern], attrs)  # type: ignore[list-item]

    def load_from_morph_rules(
        self, morph_rules: Dict[str, Dict[str, Dict[Union[int, str], Union[int, str]]]]
    ) -> None:
        """Load attribute ruler patterns from morph rules.

        morph_rules (dict): The morph rules that map token text and
            fine-grained tags to coarse-grained tags, lemmas and morphological
            features.

        DOCS: https://spacy.io/api/attributeruler#load_from_morph_rules
        """
        for tag in morph_rules:
            for word in morph_rules[tag]:
                pattern = [{"ORTH": word, "TAG": tag}]
                attrs = morph_rules[tag][word]
                attrs, morph_attrs = _split_morph_attrs(attrs)
                if "MORPH" in attrs:
                    morph = self.vocab.morphology.add(attrs["MORPH"])
                    attrs["MORPH"] = self.vocab.strings[morph]
                elif morph_attrs:
                    morph = self.vocab.morphology.add(morph_attrs)
                    attrs["MORPH"] = self.vocab.strings[morph]
                self.add([pattern], attrs)  # type: ignore[list-item]

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

        DOCS: https://spacy.io/api/attributeruler#add
        """
        # We need to make a string here, because otherwise the ID we pass back
        # will be interpreted as the hash of a string, rather than an ordinal.
        key = str(len(self.attrs))
        self.matcher.add(self.vocab.strings.add(key), patterns)  # type: ignore[arg-type]
        self._attrs_unnormed.append(attrs)
        attrs = normalize_token_attrs(self.vocab, attrs)
        self.attrs.append(attrs)
        self.indices.append(index)

    def add_patterns(self, patterns: Iterable[AttributeRulerPatternType]) -> None:
        """Add patterns from a list of pattern dicts with the keys as the
        arguments to AttributeRuler.add.
        patterns (Iterable[dict]): A list of pattern dicts with the keys
            as the arguments to AttributeRuler.add (patterns/attrs/index) to
            add as patterns.

        DOCS: https://spacy.io/api/attributeruler#add_patterns
        """
        for p in patterns:
            self.add(**p)  # type: ignore[arg-type]

    @property
    def patterns(self) -> List[AttributeRulerPatternType]:
        """All the added patterns."""
        all_patterns = []
        for i in range(len(self.attrs)):
            p = {}
            p["patterns"] = self.matcher.get(str(i))[1]
            p["attrs"] = self._attrs_unnormed[i]  # type: ignore
            p["index"] = self.indices[i]  # type: ignore
            all_patterns.append(p)
        return all_patterns  # type: ignore[return-value]

    def to_bytes(self, exclude: Iterable[str] = SimpleFrozenList()) -> bytes:
        """Serialize the AttributeRuler to a bytestring.

        exclude (Iterable[str]): String names of serialization fields to exclude.
        RETURNS (bytes): The serialized object.

        DOCS: https://spacy.io/api/attributeruler#to_bytes
        """
        serialize = {}
        serialize["vocab"] = lambda: self.vocab.to_bytes(exclude=exclude)
        serialize["patterns"] = lambda: srsly.msgpack_dumps(self.patterns)
        return util.to_bytes(serialize, exclude)

    def from_bytes(
        self, bytes_data: bytes, exclude: Iterable[str] = SimpleFrozenList()
    ) -> "AttributeRuler":
        """Load the AttributeRuler from a bytestring.

        bytes_data (bytes): The data to load.
        exclude (Iterable[str]): String names of serialization fields to exclude.
        returns (AttributeRuler): The loaded object.

        DOCS: https://spacy.io/api/attributeruler#from_bytes
        """

        def load_patterns(b):
            self.add_patterns(srsly.msgpack_loads(b))

        deserialize = {
            "vocab": lambda b: self.vocab.from_bytes(b, exclude=exclude),
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

        DOCS: https://spacy.io/api/attributeruler#to_disk
        """
        serialize = {
            "vocab": lambda p: self.vocab.to_disk(p, exclude=exclude),
            "patterns": lambda p: srsly.write_msgpack(p, self.patterns),
        }
        util.to_disk(path, serialize, exclude)

    def from_disk(
        self, path: Union[Path, str], exclude: Iterable[str] = SimpleFrozenList()
    ) -> "AttributeRuler":
        """Load the AttributeRuler from disk.

        path (Union[Path, str]): A path to a directory.
        exclude (Iterable[str]): String names of serialization fields to exclude.
        RETURNS (AttributeRuler): The loaded object.

        DOCS: https://spacy.io/api/attributeruler#from_disk
        """

        def load_patterns(p):
            self.add_patterns(srsly.read_msgpack(p))

        deserialize = {
            "vocab": lambda p: self.vocab.from_disk(p, exclude=exclude),
            "patterns": load_patterns,
        }
        util.from_disk(path, deserialize, exclude)
        return self


def _split_morph_attrs(attrs: dict) -> Tuple[dict, dict]:
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

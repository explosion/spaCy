from typing import Optional, Union, List, Dict, Tuple, Iterable, Any, Callable
from typing import Sequence, Set, cast
import warnings
from functools import partial
from pathlib import Path
import srsly

from .pipe import Pipe
from ..training import Example
from ..language import Language
from ..errors import Errors, Warnings
from ..util import ensure_path, SimpleFrozenList, registry
from ..tokens import Doc, Span
from ..scorer import Scorer
from ..matcher import Matcher, PhraseMatcher
from .. import util

PatternType = Dict[str, Union[str, List[Dict[str, Any]]]]
DEFAULT_SPANS_KEY = "ruler"


@Language.factory(
    "future_entity_ruler",
    assigns=["doc.ents"],
    default_config={
        "phrase_matcher_attr": None,
        "validate": False,
        "overwrite_ents": False,
        "scorer": {"@scorers": "spacy.entity_ruler_scorer.v1"},
        "ent_id_sep": "__unused__",
    },
    default_score_weights={
        "ents_f": 1.0,
        "ents_p": 0.0,
        "ents_r": 0.0,
        "ents_per_type": None,
    },
)
def make_entity_ruler(
    nlp: Language,
    name: str,
    phrase_matcher_attr: Optional[Union[int, str]],
    validate: bool,
    overwrite_ents: bool,
    scorer: Optional[Callable],
    ent_id_sep: str,
):
    if overwrite_ents:
        ents_filter = prioritize_new_ents_filter
    else:
        ents_filter = prioritize_existing_ents_filter
    return SpanRuler(
        nlp,
        name,
        spans_key=None,
        spans_filter=None,
        annotate_ents=True,
        ents_filter=ents_filter,
        phrase_matcher_attr=phrase_matcher_attr,
        validate=validate,
        overwrite=False,
        scorer=scorer,
    )


@Language.factory(
    "span_ruler",
    assigns=["doc.spans"],
    default_config={
        "spans_key": DEFAULT_SPANS_KEY,
        "spans_filter": None,
        "annotate_ents": False,
        "ents_filter": {"@misc": "spacy.first_longest_spans_filter.v1"},
        "phrase_matcher_attr": None,
        "validate": False,
        "overwrite": True,
        "scorer": {
            "@scorers": "spacy.overlapping_labeled_spans_scorer.v1",
            "spans_key": DEFAULT_SPANS_KEY,
        },
    },
    default_score_weights={
        f"spans_{DEFAULT_SPANS_KEY}_f": 1.0,
        f"spans_{DEFAULT_SPANS_KEY}_p": 0.0,
        f"spans_{DEFAULT_SPANS_KEY}_r": 0.0,
        f"spans_{DEFAULT_SPANS_KEY}_per_type": None,
    },
)
def make_span_ruler(
    nlp: Language,
    name: str,
    spans_key: Optional[str],
    spans_filter: Optional[Callable[[Iterable[Span], Iterable[Span]], Iterable[Span]]],
    annotate_ents: bool,
    ents_filter: Callable[[Iterable[Span], Iterable[Span]], Iterable[Span]],
    phrase_matcher_attr: Optional[Union[int, str]],
    validate: bool,
    overwrite: bool,
    scorer: Optional[Callable],
):
    return SpanRuler(
        nlp,
        name,
        spans_key=spans_key,
        spans_filter=spans_filter,
        annotate_ents=annotate_ents,
        ents_filter=ents_filter,
        phrase_matcher_attr=phrase_matcher_attr,
        validate=validate,
        overwrite=overwrite,
        scorer=scorer,
    )


def prioritize_new_ents_filter(
    entities: Iterable[Span], spans: Iterable[Span]
) -> List[Span]:
    """Merge entities and spans into one list without overlaps by allowing
    spans to overwrite any entities that they overlap with. Intended to
    replicate the overwrite_ents=True behavior from the EntityRuler.

    entities (Iterable[Span]): The entities, already filtered for overlaps.
    spans (Iterable[Span]): The spans to merge, may contain overlaps.
    RETURNS (List[Span]): Filtered list of non-overlapping spans.
    """
    get_sort_key = lambda span: (span.end - span.start, -span.start)
    spans = sorted(spans, key=get_sort_key, reverse=True)
    entities = list(entities)
    new_entities = []
    seen_tokens: Set[int] = set()
    for span in spans:
        start = span.start
        end = span.end
        if all(token.i not in seen_tokens for token in span):
            new_entities.append(span)
            entities = [e for e in entities if not (e.start < end and e.end > start)]
            seen_tokens.update(range(start, end))
    return entities + new_entities


@registry.misc("spacy.prioritize_new_ents_filter.v1")
def make_prioritize_new_ents_filter():
    return prioritize_new_ents_filter


def prioritize_existing_ents_filter(
    entities: Iterable[Span], spans: Iterable[Span]
) -> List[Span]:
    """Merge entities and spans into one list without overlaps by prioritizing
    existing entities. Intended to replicate the overwrite_ents=False behavior
    from the EntityRuler.

    entities (Iterable[Span]): The entities, already filtered for overlaps.
    spans (Iterable[Span]): The spans to merge, may contain overlaps.
    RETURNS (List[Span]): Filtered list of non-overlapping spans.
    """
    get_sort_key = lambda span: (span.end - span.start, -span.start)
    spans = sorted(spans, key=get_sort_key, reverse=True)
    entities = list(entities)
    new_entities = []
    seen_tokens: Set[int] = set()
    seen_tokens.update(*(range(ent.start, ent.end) for ent in entities))
    for span in spans:
        start = span.start
        end = span.end
        if all(token.i not in seen_tokens for token in span):
            new_entities.append(span)
            seen_tokens.update(range(start, end))
    return entities + new_entities


@registry.misc("spacy.prioritize_existing_ents_filter.v1")
def make_preverse_existing_ents_filter():
    return prioritize_existing_ents_filter


def overlapping_labeled_spans_score(
    examples: Iterable[Example], *, spans_key=DEFAULT_SPANS_KEY, **kwargs
) -> Dict[str, Any]:
    kwargs = dict(kwargs)
    attr_prefix = f"spans_"
    kwargs.setdefault("attr", f"{attr_prefix}{spans_key}")
    kwargs.setdefault("allow_overlap", True)
    kwargs.setdefault("labeled", True)
    kwargs.setdefault(
        "getter", lambda doc, key: doc.spans.get(key[len(attr_prefix) :], [])
    )
    kwargs.setdefault("has_annotation", lambda doc: spans_key in doc.spans)
    return Scorer.score_spans(examples, **kwargs)


@registry.scorers("spacy.overlapping_labeled_spans_scorer.v1")
def make_overlapping_labeled_spans_scorer(spans_key: str = DEFAULT_SPANS_KEY):
    return partial(overlapping_labeled_spans_score, spans_key=spans_key)


class SpanRuler(Pipe):
    """The SpanRuler lets you add spans to the `Doc.spans` using token-based
    rules or exact phrase matches.

    DOCS: https://spacy.io/api/spanruler
    USAGE: https://spacy.io/usage/rule-based-matching#spanruler
    """

    def __init__(
        self,
        nlp: Language,
        name: str = "span_ruler",
        *,
        spans_key: Optional[str] = DEFAULT_SPANS_KEY,
        spans_filter: Optional[
            Callable[[Iterable[Span], Iterable[Span]], Iterable[Span]]
        ] = None,
        annotate_ents: bool = False,
        ents_filter: Callable[
            [Iterable[Span], Iterable[Span]], Iterable[Span]
        ] = util.filter_chain_spans,
        phrase_matcher_attr: Optional[Union[int, str]] = None,
        validate: bool = False,
        overwrite: bool = False,
        scorer: Optional[Callable] = partial(
            overlapping_labeled_spans_score, spans_key=DEFAULT_SPANS_KEY
        ),
    ) -> None:
        """Initialize the span ruler. If patterns are supplied here, they
        need to be a list of dictionaries with a `"label"` and `"pattern"`
        key. A pattern can either be a token pattern (list) or a phrase pattern
        (string). For example: `{'label': 'ORG', 'pattern': 'Apple'}`.

        nlp (Language): The shared nlp object to pass the vocab to the matchers
            and process phrase patterns.
        name (str): Instance name of the current pipeline component. Typically
            passed in automatically from the factory when the component is
            added. Used to disable the current span ruler while creating
            phrase patterns with the nlp object.
        spans_key (Optional[str]): The spans key to save the spans under. If
            `None`, no spans are saved. Defaults to "ruler".
        spans_filter (Optional[Callable[[Iterable[Span], Iterable[Span]], List[Span]]):
            The optional method to filter spans before they are assigned to
            doc.spans. Defaults to `None`.
        annotate_ents (bool): Whether to save spans to doc.ents. Defaults to
            `False`.
        ents_filter (Callable[[Iterable[Span], Iterable[Span]], List[Span]]):
            The method to filter spans before they are assigned to doc.ents.
            Defaults to `util.filter_chain_spans`.
        phrase_matcher_attr (Optional[Union[int, str]]): Token attribute to
            match on, passed to the internal PhraseMatcher as `attr`. Defaults
            to `None`.
        validate (bool): Whether patterns should be validated, passed to
            Matcher and PhraseMatcher as `validate`.
        overwrite (bool): Whether to remove any existing spans under this spans
            key if `spans_key` is set, and/or to remove any ents under `doc.ents` if
            `annotate_ents` is set. Defaults to `True`.
        scorer (Optional[Callable]): The scoring method. Defaults to
            spacy.pipeline.span_ruler.overlapping_labeled_spans_score.

        DOCS: https://spacy.io/api/spanruler#init
        """
        self.nlp = nlp
        self.name = name
        self.spans_key = spans_key
        self.annotate_ents = annotate_ents
        self.phrase_matcher_attr = phrase_matcher_attr
        self.validate = validate
        self.overwrite = overwrite
        self.spans_filter = spans_filter
        self.ents_filter = ents_filter
        self.scorer = scorer
        self._match_label_id_map: Dict[int, Dict[str, str]] = {}
        self.clear()

    def __len__(self) -> int:
        """The number of all labels added to the span ruler."""
        return len(self._patterns)

    def __contains__(self, label: str) -> bool:
        """Whether a label is present in the patterns."""
        for label_id in self._match_label_id_map.values():
            if label_id["label"] == label:
                return True
        return False

    @property
    def key(self) -> Optional[str]:
        """Key of the doc.spans dict to save the spans under."""
        return self.spans_key

    def __call__(self, doc: Doc) -> Doc:
        """Find matches in document and add them as entities.

        doc (Doc): The Doc object in the pipeline.
        RETURNS (Doc): The Doc with added entities, if available.

        DOCS: https://spacy.io/api/spanruler#call
        """
        error_handler = self.get_error_handler()
        try:
            matches = self.match(doc)
            self.set_annotations(doc, matches)
            return doc
        except Exception as e:
            return error_handler(self.name, self, [doc], e)

    def match(self, doc: Doc):
        self._require_patterns()
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="\\[W036")
            matches = cast(
                List[Tuple[int, int, int]],
                list(self.matcher(doc)) + list(self.phrase_matcher(doc)),
            )
        deduplicated_matches = set(
            Span(
                doc,
                start,
                end,
                label=self._match_label_id_map[m_id]["label"],
                span_id=self._match_label_id_map[m_id]["id"],
            )
            for m_id, start, end in matches
            if start != end
        )
        return sorted(list(deduplicated_matches))

    def set_annotations(self, doc, matches):
        """Modify the document in place"""
        # set doc.spans if spans_key is set
        if self.key:
            spans = []
            if self.key in doc.spans and not self.overwrite:
                spans = doc.spans[self.key]
            spans.extend(
                self.spans_filter(spans, matches) if self.spans_filter else matches
            )
            doc.spans[self.key] = spans
        # set doc.ents if annotate_ents is set
        if self.annotate_ents:
            spans = []
            if not self.overwrite:
                spans = list(doc.ents)
            spans = self.ents_filter(spans, matches)
            try:
                doc.ents = sorted(spans)
            except ValueError:
                raise ValueError(Errors.E854)

    @property
    def labels(self) -> Tuple[str, ...]:
        """All labels present in the match patterns.

        RETURNS (set): The string labels.

        DOCS: https://spacy.io/api/spanruler#labels
        """
        return tuple(sorted(set([cast(str, p["label"]) for p in self._patterns])))

    @property
    def ids(self) -> Tuple[str, ...]:
        """All IDs present in the match patterns.

        RETURNS (set): The string IDs.

        DOCS: https://spacy.io/api/spanruler#ids
        """
        return tuple(
            sorted(set([cast(str, p.get("id")) for p in self._patterns]) - set([None]))
        )

    def initialize(
        self,
        get_examples: Callable[[], Iterable[Example]],
        *,
        nlp: Optional[Language] = None,
        patterns: Optional[Sequence[PatternType]] = None,
    ):
        """Initialize the pipe for training.

        get_examples (Callable[[], Iterable[Example]]): Function that
            returns a representative sample of gold-standard Example objects.
        nlp (Language): The current nlp object the component is part of.
        patterns (Optional[Iterable[PatternType]]): The list of patterns.

        DOCS: https://spacy.io/api/spanruler#initialize
        """
        self.clear()
        if patterns:
            self.add_patterns(patterns)  # type: ignore[arg-type]

    @property
    def patterns(self) -> List[PatternType]:
        """Get all patterns that were added to the span ruler.

        RETURNS (list): The original patterns, one dictionary per pattern.

        DOCS: https://spacy.io/api/spanruler#patterns
        """
        return self._patterns

    def add_patterns(self, patterns: List[PatternType]) -> None:
        """Add patterns to the span ruler. A pattern can either be a token
        pattern (list of dicts) or a phrase pattern (string). For example:
        {'label': 'ORG', 'pattern': 'Apple'}
        {'label': 'ORG', 'pattern': 'Apple', 'id': 'apple'}
        {'label': 'GPE', 'pattern': [{'lower': 'san'}, {'lower': 'francisco'}]}

        patterns (list): The patterns to add.

        DOCS: https://spacy.io/api/spanruler#add_patterns
        """

        # disable the nlp components after this one in case they haven't been
        # initialized / deserialized yet
        try:
            current_index = -1
            for i, (name, pipe) in enumerate(self.nlp.pipeline):
                if self == pipe:
                    current_index = i
                    break
            subsequent_pipes = [pipe for pipe in self.nlp.pipe_names[current_index:]]
        except ValueError:
            subsequent_pipes = []
        with self.nlp.select_pipes(disable=subsequent_pipes):
            phrase_pattern_labels = []
            phrase_pattern_texts = []
            for entry in patterns:
                p_label = cast(str, entry["label"])
                p_id = cast(str, entry.get("id", ""))
                label = repr((p_label, p_id))
                self._match_label_id_map[self.nlp.vocab.strings.as_int(label)] = {
                    "label": p_label,
                    "id": p_id,
                }
                if isinstance(entry["pattern"], str):
                    phrase_pattern_labels.append(label)
                    phrase_pattern_texts.append(entry["pattern"])
                elif isinstance(entry["pattern"], list):
                    self.matcher.add(label, [entry["pattern"]])
                else:
                    raise ValueError(Errors.E097.format(pattern=entry["pattern"]))
                self._patterns.append(entry)
            for label, pattern in zip(
                phrase_pattern_labels,
                self.nlp.pipe(phrase_pattern_texts),
            ):
                self.phrase_matcher.add(label, [pattern])

    def clear(self) -> None:
        """Reset all patterns.

        RETURNS: None
        DOCS: https://spacy.io/api/spanruler#clear
        """
        self._patterns: List[PatternType] = []
        self.matcher: Matcher = Matcher(self.nlp.vocab, validate=self.validate)
        self.phrase_matcher: PhraseMatcher = PhraseMatcher(
            self.nlp.vocab,
            attr=self.phrase_matcher_attr,
            validate=self.validate,
        )

    def remove(self, label: str) -> None:
        """Remove a pattern by its label.

        label (str): Label of the pattern to be removed.
        RETURNS: None
        DOCS: https://spacy.io/api/spanruler#remove
        """
        if label not in self:
            raise ValueError(
                Errors.E1024.format(attr_type="label", label=label, component=self.name)
            )
        self._patterns = [p for p in self._patterns if p["label"] != label]
        for m_label in self._match_label_id_map:
            if self._match_label_id_map[m_label]["label"] == label:
                m_label_str = self.nlp.vocab.strings.as_string(m_label)
                if m_label_str in self.phrase_matcher:
                    self.phrase_matcher.remove(m_label_str)
                if m_label_str in self.matcher:
                    self.matcher.remove(m_label_str)

    def remove_by_id(self, pattern_id: str) -> None:
        """Remove a pattern by its pattern ID.

        pattern_id (str): ID of the pattern to be removed.
        RETURNS: None
        DOCS: https://spacy.io/api/spanruler#remove_by_id
        """
        orig_len = len(self)
        self._patterns = [p for p in self._patterns if p.get("id") != pattern_id]
        if orig_len == len(self):
            raise ValueError(
                Errors.E1024.format(
                    attr_type="ID", label=pattern_id, component=self.name
                )
            )
        for m_label in self._match_label_id_map:
            if self._match_label_id_map[m_label]["id"] == pattern_id:
                m_label_str = self.nlp.vocab.strings.as_string(m_label)
                if m_label_str in self.phrase_matcher:
                    self.phrase_matcher.remove(m_label_str)
                if m_label_str in self.matcher:
                    self.matcher.remove(m_label_str)

    def _require_patterns(self) -> None:
        """Raise a warning if this component has no patterns defined."""
        if len(self) == 0:
            warnings.warn(Warnings.W036.format(name=self.name))

    def from_bytes(
        self, bytes_data: bytes, *, exclude: Iterable[str] = SimpleFrozenList()
    ) -> "SpanRuler":
        """Load the span ruler from a bytestring.

        bytes_data (bytes): The bytestring to load.
        RETURNS (SpanRuler): The loaded span ruler.

        DOCS: https://spacy.io/api/spanruler#from_bytes
        """
        self.clear()
        deserializers = {
            "patterns": lambda b: self.add_patterns(srsly.json_loads(b)),
        }
        util.from_bytes(bytes_data, deserializers, exclude)
        return self

    def to_bytes(self, *, exclude: Iterable[str] = SimpleFrozenList()) -> bytes:
        """Serialize the span ruler to a bytestring.

        RETURNS (bytes): The serialized patterns.

        DOCS: https://spacy.io/api/spanruler#to_bytes
        """
        serializers = {
            "patterns": lambda: srsly.json_dumps(self.patterns),
        }
        return util.to_bytes(serializers, exclude)

    def from_disk(
        self, path: Union[str, Path], *, exclude: Iterable[str] = SimpleFrozenList()
    ) -> "SpanRuler":
        """Load the span ruler from a directory.

        path (Union[str, Path]): A path to a directory.
        RETURNS (SpanRuler): The loaded span ruler.

        DOCS: https://spacy.io/api/spanruler#from_disk
        """
        self.clear()
        path = ensure_path(path)
        deserializers = {
            "patterns": lambda p: self.add_patterns(srsly.read_jsonl(p)),
        }
        util.from_disk(path, deserializers, {})
        return self

    def to_disk(
        self, path: Union[str, Path], *, exclude: Iterable[str] = SimpleFrozenList()
    ) -> None:
        """Save the span ruler patterns to a directory.

        path (Union[str, Path]): A path to a directory.

        DOCS: https://spacy.io/api/spanruler#to_disk
        """
        path = ensure_path(path)
        serializers = {
            "patterns": lambda p: srsly.write_jsonl(p, self.patterns),
        }
        util.to_disk(path, serializers, {})

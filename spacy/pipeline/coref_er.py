from typing import Optional, Union, Iterable, Callable, List, Dict, Any
from pathlib import Path
import srsly

from .pipe import Pipe
from ..scorer import Scorer
from ..training import Example
from ..language import Language
from ..tokens import Doc, Span, SpanGroup
from ..matcher import Matcher
from ..util import ensure_path, to_disk, from_disk, SimpleFrozenList


DEFAULT_MENTIONS = "coref_mentions"
DEFAULT_MATCHER_KEY = "POS"
DEFAULT_MATCHER_VALUES = ["PROPN", "PRON"]


@Language.factory(
    "coref_er",
    assigns=[f"doc.spans"],
    requires=["doc.ents", "token.ent_iob", "token.ent_type", "token.pos"],
    default_config={
        "span_mentions": DEFAULT_MENTIONS,
        "matcher_key": DEFAULT_MATCHER_KEY,
        "matcher_values": DEFAULT_MATCHER_VALUES,
    },
    default_score_weights={
        "coref_mentions_f": None,
        "coref_mentions_p": None,
        "coref_mentions_r": 1.0,  # the mentions data needs to be consistently annotated for precision rates to make sense
    },
)
def make_coref_er(nlp: Language, name: str, span_mentions: str, matcher_key: str, matcher_values: List[str]):
    return CorefEntityRecognizer(
        nlp, name, span_mentions=span_mentions, matcher_key=matcher_key, matcher_values=matcher_values
    )


class CorefEntityRecognizer(Pipe):
    """TODO.

        DOCS: https://spacy.io/api/coref_er (TODO)
        USAGE: https://spacy.io/usage (TODO)
        """

    def __init__(
        self,
        nlp: Language,
        name: str = "coref_er",
        *,
        span_mentions: str,
        matcher_key: str,
        matcher_values: List[str],
    ) -> None:
        """Initialize the entity recognizer for coreference mentions. TODO

        nlp (Language): The shared nlp object.
        name (str): Instance name of the current pipeline component. Typically
            passed in automatically from the factory when the component is
            added.
        span_mentions (str): Key in doc.spans to store the coref mentions in.
        matcher_key (List[str]): Field for the matcher to work on (e.g. "POS" or "TAG")
        matcher_values (List[str]): Values to match token sequences as
            plausible coref mentions

        DOCS: https://spacy.io/api/coref_er#init (TODO)
        """
        self.nlp = nlp
        self.name = name
        self.span_mentions = span_mentions
        self.matcher_key = matcher_key
        self.matcher_values = matcher_values
        self.matcher = Matcher(nlp.vocab)
        # TODO: allow to specify any matcher patterns instead?
        for value in matcher_values:
            self.matcher.add(
                f"{value}_SEQ", [[{matcher_key: value, "OP": "+"}]], greedy="LONGEST"
            )

    @staticmethod
    def _string_offset(span: Span):
        return f"{span.start}-{span.end}"

    def __call__(self, doc: Doc) -> Doc:
        """Find relevant coref mentions in the document and add them
        to the doc's relevant span container.

        doc (Doc): The Doc object in the pipeline.
        RETURNS (Doc): The Doc with added entities, if available.

        DOCS: https://spacy.io/api/coref_er#call (TODO)
        """
        error_handler = self.get_error_handler()
        try:
            # Add NER
            spans = list(doc.ents)
            offsets = set()
            offsets.update([self._string_offset(e) for e in doc.ents])

            # pronouns and proper nouns
            try:
                matches = self.matcher(doc, as_spans=True)
            except ValueError:
                raise ValueError(f"Could not run the matcher for 'coref_er'. If {self.matcher_key} tags "
                                 "are not available, change the 'matcher_key' in the config, "
                                 "or set matcher_values to an empty list.")
            spans.extend([m for m in matches if self._string_offset(m) not in offsets])
            offsets.update([self._string_offset(m) for m in matches])

            # noun_chunks - only if implemented and parsing information is available
            try:
                spans.extend(
                    [nc for nc in doc.noun_chunks if self._string_offset(nc) not in offsets]
                )
                offsets.update([self._string_offset(nc) for nc in doc.noun_chunks])
            except (NotImplementedError, ValueError):
                pass

            self.set_annotations(doc, spans)
            return doc
        except Exception as e:
            error_handler(self.name, self, [doc], e)

    def set_annotations(self, doc, spans):
        """Modify the document in place"""
        group = SpanGroup(doc, name=self.span_mentions, spans=spans)
        if self.span_mentions in doc.spans:
            raise ValueError(f"Couldn't store the results of {self.name}, as the key "
                             f"{self.span_mentions} already exists in 'doc.spans'.")
        doc.spans[self.span_mentions] = group

    def initialize(
        self,
        get_examples: Callable[[], Iterable[Example]],
        *,
        nlp: Optional[Language] = None,
    ):
        """Initialize the pipe for training.

        get_examples (Callable[[], Iterable[Example]]): Function that
            returns a representative sample of gold-standard Example objects.
        nlp (Language): The current nlp object the component is part of.

        DOCS: https://spacy.io/api/coref_er#initialize (TODO)
        """
        pass

    def from_bytes(
        self, bytes_data: bytes, *, exclude: Iterable[str] = SimpleFrozenList()
    ) -> "CorefEntityRecognizer":
        """Load the coreference entity recognizer from a bytestring.

        bytes_data (bytes): The bytestring to load.
        RETURNS (CorefEntityRecognizer): The loaded coreference entity recognizer.

        DOCS: https://spacy.io/api/coref_er#from_bytes
        """
        cfg = srsly.msgpack_loads(bytes_data)
        self.span_mentions = cfg.get("span_mentions", DEFAULT_MENTIONS)
        self.matcher_key = cfg.get("matcher_key", DEFAULT_MATCHER_KEY)
        self.matcher_values = cfg.get("matcher_values", DEFAULT_MATCHER_VALUES)
        return self

    def to_bytes(self, *, exclude: Iterable[str] = SimpleFrozenList()) -> bytes:
        """Serialize the coreference entity recognizer to a bytestring.

        RETURNS (bytes): The serialized component.

        DOCS: https://spacy.io/api/coref_er#to_bytes (TODO)
        """
        serial = {"span_mentions": self.span_mentions}
        return srsly.msgpack_dumps(serial)

    def from_disk(
        self, path: Union[str, Path], *, exclude: Iterable[str] = SimpleFrozenList()
    ) -> "CorefEntityRecognizer":
        """Load the coreference entity recognizer  from a file.

        path (str / Path): The JSONL file to load.
        RETURNS (CorefEntityRecognizer): The loaded coreference entity recognizer .

        DOCS: https://spacy.io/api/coref_er#from_disk (TODO)
        """
        path = ensure_path(path)
        cfg = {}
        deserializers_cfg = {"cfg": lambda p: cfg.update(srsly.read_json(p))}
        from_disk(path, deserializers_cfg, {})
        self.span_mentions = cfg.get("span_mentions", DEFAULT_MENTIONS)
        self.matcher_key = cfg.get("matcher_key", DEFAULT_MATCHER_KEY)
        self.matcher_values = cfg.get("matcher_values", DEFAULT_MATCHER_VALUES)
        return self

    def to_disk(
        self, path: Union[str, Path], *, exclude: Iterable[str] = SimpleFrozenList()
    ) -> None:
        """Save the coreference entity recognizer to a directory.

        path (str / Path): The JSONL file to save.

        DOCS: https://spacy.io/api/coref_er#to_disk (TODO)
        """
        path = ensure_path(path)
        cfg = {
            "span_mentions": self.span_mentions,
            "matcher_key": self.matcher_key,
            "matcher_values": self.matcher_values,
        }
        serializers = {"cfg": lambda p: srsly.write_json(p, cfg)}
        to_disk(path, serializers, {})

    def score(self, examples: Iterable[Example], **kwargs) -> Dict[str, Any]:
        """Score a batch of examples.

        examples (Iterable[Example]): The examples to score.
        RETURNS (Dict[str, Any]): The scores, produced by Scorer.score_coref.

        DOCS: https://spacy.io/api/coref_er#score (TODO)
        """
        def mentions_getter(doc, span_key):
            return doc.spans[span_key]
        # This will work better once PR 7209 is merged
        kwargs.setdefault("getter", mentions_getter)
        kwargs.setdefault("attr", self.span_mentions)
        kwargs.setdefault("include_label", False)
        kwargs.setdefault("allow_overlap", True)
        return Scorer.score_spans(examples, **kwargs)

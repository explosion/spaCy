# coding: utf8
from __future__ import unicode_literals

from collections import defaultdict, OrderedDict
import srsly

from ..errors import Errors
from ..compat import basestring_
from ..util import ensure_path, to_disk, from_disk
from ..tokens import Span
from ..matcher import Matcher, PhraseMatcher

DEFAULT_ENT_ID_SEP = "||"


class EntityRuler(object):
    """The EntityRuler lets you add spans to the `Doc.ents` using token-based
    rules or exact phrase matches. It can be combined with the statistical
    `EntityRecognizer` to boost accuracy, or used on its own to implement a
    purely rule-based entity recognition system. After initialization, the
    component is typically added to the pipeline using `nlp.add_pipe`.

    DOCS: https://spacy.io/api/entityruler
    USAGE: https://spacy.io/usage/rule-based-matching#entityruler
    """

    name = "entity_ruler"

    def __init__(self, nlp, phrase_matcher_attr=None, **cfg):
        """Initialize the entitiy ruler. If patterns are supplied here, they
        need to be a list of dictionaries with a `"label"` and `"pattern"`
        key. A pattern can either be a token pattern (list) or a phrase pattern
        (string). For example: `{'label': 'ORG', 'pattern': 'Apple'}`.

        nlp (Language): The shared nlp object to pass the vocab to the matchers
            and process phrase patterns.
        phrase_matcher_attr (int / unicode): Token attribute to match on, passed
            to the internal PhraseMatcher as `attr`
        patterns (iterable): Optional patterns to load in.
        overwrite_ents (bool): If existing entities are present, e.g. entities
            added by the model, overwrite them by matches if necessary.
        **cfg: Other config parameters. If pipeline component is loaded as part
            of a model pipeline, this will include all keyword arguments passed
            to `spacy.load`.
        RETURNS (EntityRuler): The newly constructed object.

        DOCS: https://spacy.io/api/entityruler#init
        """
        self.nlp = nlp
        self.overwrite = cfg.get("overwrite_ents", False)
        self.token_patterns = defaultdict(list)
        self.phrase_patterns = defaultdict(list)
        self.matcher = Matcher(nlp.vocab)
        if phrase_matcher_attr is not None:
            self.phrase_matcher_attr = phrase_matcher_attr
            self.phrase_matcher = PhraseMatcher(
                nlp.vocab, attr=self.phrase_matcher_attr
            )
        else:
            self.phrase_matcher_attr = None
            self.phrase_matcher = PhraseMatcher(nlp.vocab)
        self.ent_id_sep = cfg.get("ent_id_sep", DEFAULT_ENT_ID_SEP)
        patterns = cfg.get("patterns")
        if patterns is not None:
            self.add_patterns(patterns)

    def __len__(self):
        """The number of all patterns added to the entity ruler."""
        n_token_patterns = sum(len(p) for p in self.token_patterns.values())
        n_phrase_patterns = sum(len(p) for p in self.phrase_patterns.values())
        return n_token_patterns + n_phrase_patterns

    def __contains__(self, label):
        """Whether a label is present in the patterns."""
        return label in self.token_patterns or label in self.phrase_patterns

    def __call__(self, doc):
        """Find matches in document and add them as entities.

        doc (Doc): The Doc object in the pipeline.
        RETURNS (Doc): The Doc with added entities, if available.

        DOCS: https://spacy.io/api/entityruler#call
        """
        matches = list(self.matcher(doc)) + list(self.phrase_matcher(doc))
        matches = set(
            [(m_id, start, end) for m_id, start, end in matches if start != end]
        )
        get_sort_key = lambda m: (m[2] - m[1], m[1])
        matches = sorted(matches, key=get_sort_key, reverse=True)
        entities = list(doc.ents)
        new_entities = []
        seen_tokens = set()
        for match_id, start, end in matches:
            if any(t.ent_type for t in doc[start:end]) and not self.overwrite:
                continue
            # check for end - 1 here because boundaries are inclusive
            if start not in seen_tokens and end - 1 not in seen_tokens:
                if self.ent_ids:
                    label_ = self.nlp.vocab.strings[match_id]
                    ent_label, ent_id = self._split_label(label_)
                    span = Span(doc, start, end, label=ent_label)
                    if ent_id:
                        for token in span:
                            token.ent_id_ = ent_id
                else:
                    span = Span(doc, start, end, label=match_id)
                new_entities.append(span)
                entities = [
                    e for e in entities if not (e.start < end and e.end > start)
                ]
                seen_tokens.update(range(start, end))
        doc.ents = entities + new_entities
        return doc

    @property
    def labels(self):
        """All labels present in the match patterns.

        RETURNS (set): The string labels.

        DOCS: https://spacy.io/api/entityruler#labels
        """
        all_labels = set(self.token_patterns.keys())
        all_labels.update(self.phrase_patterns.keys())
        return tuple(all_labels)

    @property
    def ent_ids(self):
        """All entity ids present in the match patterns meta dicts.

        RETURNS (set): The string entity ids.

        DOCS: https://spacy.io/api/entityruler#labels
        """
        all_ent_ids = set()
        for l in self.labels:
            if self.ent_id_sep in l:
                _, ent_id = self._split_label(l)
                all_ent_ids.add(ent_id)
        return tuple(all_ent_ids)

    @property
    def patterns(self):
        """Get all patterns that were added to the entity ruler.

        RETURNS (list): The original patterns, one dictionary per pattern.

        DOCS: https://spacy.io/api/entityruler#patterns
        """
        all_patterns = []
        for label, patterns in self.token_patterns.items():
            for pattern in patterns:
                ent_label, ent_id = self._split_label(label)
                p = {"label": ent_label, "pattern": pattern}
                if ent_id:
                    p["id"] = ent_id
                all_patterns.append(p)
        for label, patterns in self.phrase_patterns.items():
            for pattern in patterns:
                ent_label, ent_id = self._split_label(label)
                p = {"label": ent_label, "pattern": pattern.text}
                if ent_id:
                    p["id"] = ent_id
                all_patterns.append(p)

        return all_patterns

    def add_patterns(self, patterns):
        """Add patterns to the entitiy ruler. A pattern can either be a token
        pattern (list of dicts) or a phrase pattern (string). For example:
        {'label': 'ORG', 'pattern': 'Apple'}
        {'label': 'GPE', 'pattern': [{'lower': 'san'}, {'lower': 'francisco'}]}

        patterns (list): The patterns to add.

        DOCS: https://spacy.io/api/entityruler#add_patterns
        """
        for entry in patterns:
            label = entry["label"]
            if "id" in entry:
                label = self._create_label(label, entry["id"])
            pattern = entry["pattern"]
            if isinstance(pattern, basestring_):
                self.phrase_patterns[label].append(self.nlp(pattern))
            elif isinstance(pattern, list):
                self.token_patterns[label].append(pattern)
            else:
                raise ValueError(Errors.E097.format(pattern=pattern))
        for label, patterns in self.token_patterns.items():
            self.matcher.add(label, None, *patterns)
        for label, patterns in self.phrase_patterns.items():
            self.phrase_matcher.add(label, None, *patterns)

    def _split_label(self, label):
        """Split Entity label into ent_label and ent_id if it contains self.ent_id_sep

        RETURNS (tuple): ent_label, ent_id
        """
        if self.ent_id_sep in label:
            ent_label, ent_id = label.rsplit(self.ent_id_sep, 1)
        else:
            ent_label = label
            ent_id = None

        return ent_label, ent_id

    def _create_label(self, label, ent_id):
        """Join Entity label with ent_id if the pattern has an `id` attribute

        RETURNS (str): The ent_label joined with configured `ent_id_sep`
        """
        if isinstance(ent_id, basestring_):
            label = "{}{}{}".format(label, self.ent_id_sep, ent_id)
        return label

    def from_bytes(self, patterns_bytes, **kwargs):
        """Load the entity ruler from a bytestring.

        patterns_bytes (bytes): The bytestring to load.
        **kwargs: Other config paramters, mostly for consistency.
        RETURNS (EntityRuler): The loaded entity ruler.

        DOCS: https://spacy.io/api/entityruler#from_bytes
        """
        cfg = srsly.msgpack_loads(patterns_bytes)
        if isinstance(cfg, dict):
            self.add_patterns(cfg.get("patterns", cfg))
            self.overwrite = cfg.get("overwrite", False)
            self.phrase_matcher_attr = cfg.get("phrase_matcher_attr", None)
            if self.phrase_matcher_attr is not None:
                self.phrase_matcher = PhraseMatcher(
                    self.nlp.vocab, attr=self.phrase_matcher_attr
                )
            self.ent_id_sep = cfg.get("ent_id_sep", DEFAULT_ENT_ID_SEP)
        else:
            self.add_patterns(cfg)
        return self

    def to_bytes(self, **kwargs):
        """Serialize the entity ruler patterns to a bytestring.

        RETURNS (bytes): The serialized patterns.

        DOCS: https://spacy.io/api/entityruler#to_bytes
        """

        serial = OrderedDict(
            (
                ("overwrite", self.overwrite),
                ("ent_id_sep", self.ent_id_sep),
                ("phrase_matcher_attr", self.phrase_matcher_attr),
                ("patterns", self.patterns),
            )
        )
        return srsly.msgpack_dumps(serial)

    def from_disk(self, path, **kwargs):
        """Load the entity ruler from a file. Expects a file containing
        newline-delimited JSON (JSONL) with one entry per line.

        path (unicode / Path): The JSONL file to load.
        **kwargs: Other config paramters, mostly for consistency.
        RETURNS (EntityRuler): The loaded entity ruler.

        DOCS: https://spacy.io/api/entityruler#from_disk
        """
        path = ensure_path(path)
        depr_patterns_path = path.with_suffix(".jsonl")
        if depr_patterns_path.is_file():
            patterns = srsly.read_jsonl(depr_patterns_path)
            self.add_patterns(patterns)
        else:
            cfg = {}
            deserializers = {
                "patterns": lambda p: self.add_patterns(
                    srsly.read_jsonl(p.with_suffix(".jsonl"))
                ),
                "cfg": lambda p: cfg.update(srsly.read_json(p)),
            }
            from_disk(path, deserializers, {})
            self.overwrite = cfg.get("overwrite", False)
            self.phrase_matcher_attr = cfg.get("phrase_matcher_attr")
            self.ent_id_sep = cfg.get("ent_id_sep", DEFAULT_ENT_ID_SEP)

            if self.phrase_matcher_attr is not None:
                self.phrase_matcher = PhraseMatcher(
                    self.nlp.vocab, attr=self.phrase_matcher_attr
                )
        return self

    def to_disk(self, path, **kwargs):
        """Save the entity ruler patterns to a directory. The patterns will be
        saved as newline-delimited JSON (JSONL).

        path (unicode / Path): The JSONL file to save.
        **kwargs: Other config paramters, mostly for consistency.
        RETURNS (EntityRuler): The loaded entity ruler.

        DOCS: https://spacy.io/api/entityruler#to_disk
        """
        path = ensure_path(path)
        cfg = {
            "overwrite": self.overwrite,
            "phrase_matcher_attr": self.phrase_matcher_attr,
            "ent_id_sep": self.ent_id_sep,
        }
        serializers = {
            "patterns": lambda p: srsly.write_jsonl(
                p.with_suffix(".jsonl"), self.patterns
            ),
            "cfg": lambda p: srsly.write_json(p, cfg),
        }
        if path.suffix == ".jsonl":  # user wants to save only JSONL
            srsly.write_jsonl(path, self.patterns)
        else:
            to_disk(path, serializers, {})

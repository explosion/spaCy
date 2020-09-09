from typing import Optional, List, Dict, Any
from thinc.api import Model

from .pipe import Pipe
from ..errors import Errors
from ..language import Language
from ..lookups import Lookups, load_lookups
from ..scorer import Scorer
from ..tokens import Doc, Token
from ..vocab import Vocab
from ..training import validate_examples
from .. import util


@Language.factory(
    "lemmatizer",
    assigns=["token.lemma"],
    default_config={
        "model": None,
        "mode": "lookup",
        "lookups": None,
        "overwrite": False,
    },
    scores=["lemma_acc"],
    default_score_weights={"lemma_acc": 1.0},
)
def make_lemmatizer(
    nlp: Language,
    model: Optional[Model],
    name: str,
    mode: str,
    lookups: Optional[Lookups],
    overwrite: bool = False,
):
    lookups = Lemmatizer.load_lookups(nlp.lang, mode, lookups)
    return Lemmatizer(
        nlp.vocab, model, name, mode=mode, lookups=lookups, overwrite=overwrite
    )


class Lemmatizer(Pipe):
    """
    The Lemmatizer supports simple part-of-speech-sensitive suffix rules and
    lookup tables.

    DOCS: https://nightly.spacy.io/api/lemmatizer
    """

    @classmethod
    def get_lookups_config(cls, mode: str) -> Dict:
        """Returns the lookups configuration settings for a given mode for use
        in Lemmatizer.load_lookups.

        mode (str): The lemmatizer mode.
        RETURNS (dict): The lookups configuration settings for this mode.

        DOCS: https://nightly.spacy.io/api/lemmatizer#get_lookups_config
        """
        if mode == "lookup":
            return {
                "required_tables": ["lemma_lookup"],
            }
        elif mode == "rule":
            return {
                "required_tables": ["lemma_rules"],
                "optional_tables": ["lemma_exc", "lemma_index"],
            }
        return {}

    @classmethod
    def load_lookups(cls, lang: str, mode: str, lookups: Optional[Lookups],) -> Lookups:
        """Load and validate lookups tables. If the provided lookups is None,
        load the default lookups tables according to the language and mode
        settings. Confirm that all required tables for the language and mode
        are present.

        lang (str): The language code.
        mode (str): The lemmatizer mode.
        lookups (Lookups): The provided lookups, may be None if the default
            lookups should be loaded.
        RETURNS (Lookups): The Lookups object.

        DOCS: https://nightly.spacy.io/api/lemmatizer#get_lookups_config
        """
        config = cls.get_lookups_config(mode)
        required_tables = config.get("required_tables", [])
        optional_tables = config.get("optional_tables", [])
        if lookups is None:
            lookups = load_lookups(lang=lang, tables=required_tables)
            optional_lookups = load_lookups(
                lang=lang, tables=optional_tables, strict=False
            )
            for table in optional_lookups.tables:
                lookups.set_table(table, optional_lookups.get_table(table))
        for table in required_tables:
            if table not in lookups:
                raise ValueError(
                    Errors.E1004.format(
                        mode=mode, tables=required_tables, found=lookups.tables
                    )
                )
        return lookups

    def __init__(
        self,
        vocab: Vocab,
        model: Optional[Model],
        name: str = "lemmatizer",
        *,
        mode: str = "lookup",
        lookups: Optional[Lookups] = None,
        overwrite: bool = False,
    ) -> None:
        """Initialize a Lemmatizer.

        vocab (Vocab): The vocab.
        model (Model): A model (not yet implemented).
        name (str): The component name. Defaults to "lemmatizer".
        mode (str): The lemmatizer mode: "lookup", "rule". Defaults to "lookup".
        lookups (Lookups): The lookups object containing the (optional) tables
            such as "lemma_rules", "lemma_index", "lemma_exc" and
            "lemma_lookup". Defaults to None
        overwrite (bool): Whether to overwrite existing lemmas. Defaults to
            `False`.

        DOCS: https://nightly.spacy.io/api/lemmatizer#init
        """
        self.vocab = vocab
        self.model = model
        self.name = name
        self._mode = mode
        self.lookups = lookups if lookups is not None else Lookups()
        self.overwrite = overwrite
        if self.mode == "lookup":
            self.lemmatize = self.lookup_lemmatize
        elif self.mode == "rule":
            self.lemmatize = self.rule_lemmatize
        else:
            mode_attr = f"{self.mode}_lemmatize"
            if not hasattr(self, mode_attr):
                raise ValueError(Errors.E1003.format(mode=mode))
            self.lemmatize = getattr(self, mode_attr)
        self.cache = {}

    @property
    def mode(self):
        return self._mode

    def __call__(self, doc: Doc) -> Doc:
        """Apply the lemmatizer to one document.

        doc (Doc): The Doc to process.
        RETURNS (Doc): The processed Doc.

        DOCS: https://nightly.spacy.io/api/lemmatizer#call
        """
        for token in doc:
            if self.overwrite or token.lemma == 0:
                token.lemma_ = self.lemmatize(token)[0]
        return doc

    def pipe(self, stream, *, batch_size=128):
        """Apply the pipe to a stream of documents. This usually happens under
        the hood when the nlp object is called on a text and all components are
        applied to the Doc.

        stream (Iterable[Doc]): A stream of documents.
        batch_size (int): The number of documents to buffer.
        YIELDS (Doc): Processed documents in order.

        DOCS: https://nightly.spacy.io/api/lemmatizer#pipe
        """
        for doc in stream:
            doc = self(doc)
            yield doc

    def lookup_lemmatize(self, token: Token) -> List[str]:
        """Lemmatize using a lookup-based approach.

        token (Token): The token to lemmatize.
        RETURNS (list): The available lemmas for the string.

        DOCS: https://nightly.spacy.io/api/lemmatizer#lookup_lemmatize
        """
        lookup_table = self.lookups.get_table("lemma_lookup", {})
        result = lookup_table.get(token.text, token.text)
        if isinstance(result, str):
            result = [result]
        return result

    def rule_lemmatize(self, token: Token) -> List[str]:
        """Lemmatize using a rule-based approach.

        token (Token): The token to lemmatize.
        RETURNS (list): The available lemmas for the string.

        DOCS: https://nightly.spacy.io/api/lemmatizer#rule_lemmatize
        """
        cache_key = (token.orth, token.pos, token.morph)
        if cache_key in self.cache:
            return self.cache[cache_key]
        string = token.text
        univ_pos = token.pos_.lower()
        if univ_pos in ("", "eol", "space"):
            return [string.lower()]
        # See Issue #435 for example of where this logic is requied.
        if self.is_base_form(token):
            return [string.lower()]
        index_table = self.lookups.get_table("lemma_index", {})
        exc_table = self.lookups.get_table("lemma_exc", {})
        rules_table = self.lookups.get_table("lemma_rules", {})
        if not any(
            (
                index_table.get(univ_pos),
                exc_table.get(univ_pos),
                rules_table.get(univ_pos),
            )
        ):
            if univ_pos == "propn":
                return [string]
            else:
                return [string.lower()]

        index = index_table.get(univ_pos, {})
        exceptions = exc_table.get(univ_pos, {})
        rules = rules_table.get(univ_pos, {})
        orig = string
        string = string.lower()
        forms = []
        oov_forms = []
        for old, new in rules:
            if string.endswith(old):
                form = string[: len(string) - len(old)] + new
                if not form:
                    pass
                elif form in index or not form.isalpha():
                    forms.append(form)
                else:
                    oov_forms.append(form)
        # Remove duplicates but preserve the ordering of applied "rules"
        forms = list(dict.fromkeys(forms))
        # Put exceptions at the front of the list, so they get priority.
        # This is a dodgy heuristic -- but it's the best we can do until we get
        # frequencies on this. We can at least prune out problematic exceptions,
        # if they shadow more frequent analyses.
        for form in exceptions.get(string, []):
            if form not in forms:
                forms.insert(0, form)
        if not forms:
            forms.extend(oov_forms)
        if not forms:
            forms.append(orig)
        self.cache[cache_key] = forms
        return forms

    def is_base_form(self, token: Token) -> bool:
        """Check whether the token is a base form that does not need further
        analysis for lemmatization.

        token (Token): The token.
        RETURNS (bool): Whether the token is a base form.

        DOCS: https://nightly.spacy.io/api/lemmatizer#is_base_form
        """
        return False

    def score(self, examples, **kwargs) -> Dict[str, Any]:
        """Score a batch of examples.

        examples (Iterable[Example]): The examples to score.
        RETURNS (Dict[str, Any]): The scores.

        DOCS: https://nightly.spacy.io/api/lemmatizer#score
        """
        validate_examples(examples, "Lemmatizer.score")
        return Scorer.score_token_attr(examples, "lemma", **kwargs)

    def to_disk(self, path, *, exclude=tuple()):
        """Save the current state to a directory.

        path (unicode or Path): A path to a directory, which will be created if
            it doesn't exist.
        exclude (list): String names of serialization fields to exclude.

        DOCS: https://nightly.spacy.io/api/vocab#to_disk
        """
        serialize = {}
        serialize["vocab"] = lambda p: self.vocab.to_disk(p)
        serialize["lookups"] = lambda p: self.lookups.to_disk(p)
        util.to_disk(path, serialize, exclude)

    def from_disk(self, path, *, exclude=tuple()):
        """Loads state from a directory. Modifies the object in place and
        returns it.

        path (unicode or Path): A path to a directory.
        exclude (list): String names of serialization fields to exclude.
        RETURNS (Vocab): The modified `Vocab` object.

        DOCS: https://nightly.spacy.io/api/vocab#to_disk
        """
        deserialize = {}
        deserialize["vocab"] = lambda p: self.vocab.from_disk(p)
        deserialize["lookups"] = lambda p: self.lookups.from_disk(p)
        util.from_disk(path, deserialize, exclude)

    def to_bytes(self, *, exclude=tuple()) -> bytes:
        """Serialize the current state to a binary string.

        exclude (list): String names of serialization fields to exclude.
        RETURNS (bytes): The serialized form of the `Vocab` object.

        DOCS: https://nightly.spacy.io/api/vocab#to_bytes
        """
        serialize = {}
        serialize["vocab"] = self.vocab.to_bytes
        serialize["lookups"] = self.lookups.to_bytes
        return util.to_bytes(serialize, exclude)

    def from_bytes(self, bytes_data: bytes, *, exclude=tuple()):
        """Load state from a binary string.

        bytes_data (bytes): The data to load from.
        exclude (list): String names of serialization fields to exclude.
        RETURNS (Vocab): The `Vocab` object.

        DOCS: https://nightly.spacy.io/api/vocab#from_bytes
        """
        deserialize = {}
        deserialize["vocab"] = lambda b: self.vocab.from_bytes(b)
        deserialize["lookups"] = lambda b: self.lookups.from_bytes(b)
        util.from_bytes(bytes_data, deserialize, exclude)

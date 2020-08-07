from typing import Optional, List, Dict

from thinc.api import Model

from .pipe import Pipe
from ..errors import Errors
from ..language import Language
from ..lookups import Lookups, load_lookups
from ..parts_of_speech import NAMES as UPOS_NAMES
from ..scorer import Scorer
from ..tokens import Doc, Token
from ..vocab import Vocab
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

    DOCS: https://spacy.io/api/lemmatizer
    """

    @classmethod
    def get_lookups_config(cls, mode: str) -> Dict:
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
            "lemma_lookup".
        """
        self.vocab = vocab
        self.model = model
        self._mode = mode
        self.lookups = lookups if lookups is not None else Lookups()
        self.overwrite = overwrite
        if self.mode == "lookup":
            self.lemmatize = self.lookup_lemmatize
        elif self.mode == "rule":
            self.lemmatize = self.rule_lemmatize
        else:
            try:
                self.lemmatize = getattr(self, f"{self.mode}_lemmatize")
            except AttributeError:
                raise ValueError(Errors.E1003.format(mode=mode))
        self.cache = {}

    @property
    def mode(self):
        return self._mode

    def __call__(self, doc: Doc) -> Doc:
        """Apply the lemmatizer to one document.

        doc (Doc): The Doc to process.
        RETURNS (Doc): The processed Doc.

        DOCS: https://spacy.io/api/lemmatizer#call
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

        DOCS: https://spacy.io/api/lemmatizer#pipe
        """
        for doc in stream:
            doc = self(doc)
            yield doc

    def lookup_lemmatize(self, token: Token) -> List[str]:
        """Lemmatize using a lookup-based approach.

        token (Token): The token to lemmatize.
        RETURNS (list): The available lemmas for the string.
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
        """
        cache_key = (token.orth, token.pos, token.morph)
        if cache_key in self.cache:
            return self.cache[cache_key]
        string = token.text
        univ_pos = token.pos_
        morphology = token.morph.to_dict()
        if isinstance(univ_pos, int):
            univ_pos = UPOS_NAMES.get(univ_pos, "X")
        univ_pos = univ_pos.lower()
        if univ_pos in ("", "eol", "space"):
            return [string.lower()]
        # See Issue #435 for example of where this logic is requied.
        if self.is_base_form(univ_pos, morphology):
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

    def is_base_form(self, univ_pos: str, morphology: Optional[dict] = None) -> bool:
        return False

    def score(self, examples, **kwargs):
        return Scorer.score_token_attr(examples, "lemma", **kwargs)

    def to_disk(self, path, *, exclude=tuple()):
        """Save the current state to a directory.

        path (unicode or Path): A path to a directory, which will be created if
            it doesn't exist.
        exclude (list): String names of serialization fields to exclude.

        DOCS: https://spacy.io/api/vocab#to_disk
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

        DOCS: https://spacy.io/api/vocab#to_disk
        """
        deserialize = {}
        deserialize["vocab"] = lambda p: self.vocab.from_disk(p)
        deserialize["lookups"] = lambda p: self.lookups.from_disk(p)
        util.from_disk(path, deserialize, exclude)

    def to_bytes(self, *, exclude=tuple()) -> bytes:
        """Serialize the current state to a binary string.

        exclude (list): String names of serialization fields to exclude.
        RETURNS (bytes): The serialized form of the `Vocab` object.

        DOCS: https://spacy.io/api/vocab#to_bytes
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

        DOCS: https://spacy.io/api/vocab#from_bytes
        """
        deserialize = {}
        deserialize["vocab"] = lambda b: self.vocab.from_bytes(b)
        deserialize["lookups"] = lambda b: self.lookups.from_bytes(b)
        util.from_bytes(bytes_data, deserialize, exclude)

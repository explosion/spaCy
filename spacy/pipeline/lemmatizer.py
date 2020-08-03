from typing import Optional, List, Any

from thinc.api import Model

from .pipe import Pipe
from ..language import Language
from ..lookups import Lookups, Table, load_lookups
from ..parts_of_speech import NAMES as UPOS_NAMES
from ..tokens import Doc, Token
from ..vocab import Vocab
from .. import util


@Language.factory(
    "lemmatizer",
    assigns=["token.lemma"],
    default_config={"model": None, "mode": "lookup", "lookups": None, "overwrite": False},
    scores=["lemma_acc"],
    default_score_weights={"lemma_acc": 1.0},
)
def make_lemmatizer(nlp: Language, model: Optional[Model], name: str, mode: str, lookups: Optional[Lookups], overwrite: bool = False):
    tables = ["lemma_lookup", "lemma_rules", "lemma_exc", "lemma_index"]
    if lookups is None:
        lookups = load_lookups(lang=nlp.lang, tables=tables)
    return Lemmatizer(nlp.vocab, model, name, mode=mode, lookups=lookups, overwrite=overwrite)


class Lemmatizer(Pipe):
    """
    The Lemmatizer supports simple part-of-speech-sensitive suffix rules and
    lookup tables.

    DOCS: https://spacy.io/api/lemmatizer
    """

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
            "lemma_rules", "lemma_index", "lemma_exc" and "lemma_lookup".
        """
        self.vocab = vocab
        self.model = model
        self.mode = mode
        self.lookups = lookups if lookups is not None else Lookups()
        self.overwrite = overwrite
        self.cache = {
            "rule": {},
        }
        self.cache_features = {
            "rule": ["ORTH", "POS"],
        }

    def __call__(self, doc: Doc) -> Doc:
        """Apply the lemmatizer to one document.

        doc (Doc): The Doc to process.
        RETURNS (Doc): The processed Doc.

        DOCS: https://spacy.io/api/lemmatizer#call
        """
        if self.cache_features.get(self.mode):
            features_array = doc.to_array(self.cache_features[self.mode])
        lemmas = []
        if self.mode == "lookup":
            for token in doc:
                lemmas.append(self.lookup_lemmatize(token)[0])
        elif self.mode == "rule":
            for i, token in enumerate(doc):
                features = tuple(features_array[i])
                if features in self.cache[self.mode]:
                    lemmas.append(self.cache[self.mode][features])
                else:
                    lemma = self.rule_lemmatize(token)[0]
                    lemmas.append(lemma)
                    self.cache[self.mode][features] = lemma
        else:
            lemmatize = getattr(self, f"{self.mode}_lemmatize")
            for token in doc:
                lemmas.append(lemmatize(token)[0])
        for token, lemma in zip(doc, lemmas):
            if self.overwrite or token.lemma == 0:
                token.lemma_ = lemma
        return doc

    def lookup_lemmatize(self, token: Token) -> List[str]:
        """Lemmatize using a lookup-based approach.

        token (Token): The token to lemmatize.
        RETURNS (list): The available lemmas for the string.
        """
        lookup_table = self.lookups.get_table("lemma_lookup", {})
        return [lookup_table.get(token.text, token.text)]

    def rule_lemmatize(self, token: Token) -> List[str]:
        """Lemmatize using a rule-based approach.

        token (Token): The token to lemmatize.
        RETURNS (list): The available lemmas for the string.
        """
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
        return forms

    def is_base_form(self, univ_pos: str, morphology: Optional[dict] = None) -> bool:
        return False

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

from typing import Optional, List, Dict, Any, Callable, Iterable, Union, Tuple, Literal
from thinc.api import Model
from pathlib import Path

import warnings

from .pipe import Pipe
from ..errors import Errors, Warnings
from ..language import Language
from ..training import Example
from ..lookups import Lookups, load_lookups
from ..scorer import Scorer
from ..tokens import Doc, Token
from ..vocab import Vocab
from ..util import logger, SimpleFrozenList, registry
from .. import util
from ..symbols import POS



@Language.factory(
    "lemmatizer",
    assigns=["token.lemma"],
    default_config={
        "model": None,
        "mode": "lookup",
        "overwrite": False,
        "scorer": {"@scorers": "spacy.lemmatizer_scorer.v1"},
    },
    default_score_weights={"lemma_acc": 1.0},
)
def make_lemmatizer(
    nlp: Language,
    model: Optional[Model],
    name: str,
    mode: str,
    overwrite: bool,
    scorer: Optional[Callable],
):
    return Lemmatizer(
        nlp.vocab, model, name, mode=mode, overwrite=overwrite, scorer=scorer
    )


def lemmatizer_score(examples: Iterable[Example], **kwargs) -> Dict[str, Any]:
    return Scorer.score_token_attr(examples, "lemma", **kwargs)


@registry.scorers("spacy.lemmatizer_scorer.v1")
def make_lemmatizer_scorer():
    return lemmatizer_score


class Lemmatizer(Pipe):
    """
    The Lemmatizer supports simple part-of-speech-sensitive suffix rules and
    lookup tables.

    DOCS: https://spacy.io/api/lemmatizer
    """

    @classmethod
    def get_lookups_config(cls, mode: str) -> Tuple[List[str], List[str]]:
        """Returns the lookups configuration settings for a given mode for use
        in Lemmatizer.load_lookups.

        mode (str): The lemmatizer mode.
        RETURNS (Tuple[List[str], List[str]]): The required and optional
            lookup tables for this mode.
        """
        if mode == "lookup":
            return (["lemma_lookup"], [])
        elif mode == "rule":
            return (["lemma_rules"], ["lemma_exc", "lemma_index"])
        return ([], [])

    def __init__(
        self,
        vocab: Vocab,
        model: Optional[Model],
        name: str = "lemmatizer",
        *,
        mode: str = "lookup",
        overwrite: bool = False,
        scorer: Optional[Callable] = lemmatizer_score,
    ) -> None:
        """Initialize a Lemmatizer.

        vocab (Vocab): The vocab.
        model (Model): A model (not yet implemented).
        name (str): The component name. Defaults to "lemmatizer".
        mode (str): The lemmatizer mode: "lookup", "rule". Defaults to "lookup".
        overwrite (bool): Whether to overwrite existing lemmas. Defaults to
            `False`.
        scorer (Optional[Callable]): The scoring method. Defaults to
            Scorer.score_token_attr for the attribute "lemma".

        DOCS: https://spacy.io/api/lemmatizer#init
        """
        self.vocab = vocab
        self.model = model
        self.name = name
        self._mode = mode
        self.lookups = Lookups()
        self.overwrite = overwrite
        self._validated = False
        if self.mode == "lookup":
            self.lemmatize = self.lookup_lemmatize
        elif self.mode == "rule":
            self.lemmatize = self.rule_lemmatize
        else:
            mode_attr = f"{self.mode}_lemmatize"
            if not hasattr(self, mode_attr):
                raise ValueError(Errors.E1003.format(mode=mode))
            self.lemmatize = getattr(self, mode_attr)
        self.cache = {}  # type: ignore[var-annotated]
        self.scorer = scorer

    @property
    def mode(self):
        return self._mode

    def __call__(self, doc: Doc) -> Doc:
        """Apply the lemmatizer to one document.

        doc (Doc): The Doc to process.
        RETURNS (Doc): The processed Doc.

        DOCS: https://spacy.io/api/lemmatizer#call
        """
        if not self._validated:
            self._validate_tables(Errors.E1004)
        error_handler = self.get_error_handler()
        try:
            for token in doc:
                if self.overwrite or token.lemma == 0:
                    token.lemma_ = self.lemmatize(token)[0]
            return doc
        except Exception as e:
            error_handler(self.name, self, [doc], e)

    def initialize(
        self,
        get_examples: Optional[Callable[[], Iterable[Example]]] = None,
        *,
        nlp: Optional[Language] = None,
        lookups: Optional[Lookups] = None,
    ):
        """Initialize the lemmatizer and load in data.

        get_examples (Callable[[], Iterable[Example]]): Function that
            returns a representative sample of gold-standard Example objects.
        nlp (Language): The current nlp object the component is part of.
        lookups (Lookups): The lookups object containing the (optional) tables
            such as "lemma_rules", "lemma_index", "lemma_exc" and
            "lemma_lookup". Defaults to None.
        """
        required_tables, optional_tables = self.get_lookups_config(self.mode)
        if lookups is None:
            logger.debug("Lemmatizer: loading tables from spacy-lookups-data")
            lookups = load_lookups(lang=self.vocab.lang, tables=required_tables)
            optional_lookups = load_lookups(
                lang=self.vocab.lang, tables=optional_tables, strict=False
            )
            for table in optional_lookups.tables:
                lookups.set_table(table, optional_lookups.get_table(table))
        self.lookups = lookups
        self._validate_tables(Errors.E1004)

    def _validate_tables(self, error_message: str = Errors.E912) -> None:
        """Check that the lookups are correct for the current mode."""
        required_tables, optional_tables = self.get_lookups_config(self.mode)
        for table in required_tables:
            if table not in self.lookups:
                raise ValueError(
                    error_message.format(
                        mode=self.mode,
                        tables=required_tables,
                        found=self.lookups.tables,
                    )
                )
        self._validated = True

    def lookup_lemmatize(self, token: Token) -> List[str]:
        """Lemmatize using a lookup-based approach.

        token (Token): The token to lemmatize.
        RETURNS (list): The available lemmas for the string.

        DOCS: https://spacy.io/api/lemmatizer#lookup_lemmatize
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

        DOCS: https://spacy.io/api/lemmatizer#rule_lemmatize
        """
        cache_key = (token.orth, token.pos, token.morph.key)  # type: ignore[attr-defined]
        if cache_key in self.cache:
            return self.cache[cache_key]
        string = token.text
        univ_pos = token.pos_.lower()
        if univ_pos in ("", "eol", "space"):
            if univ_pos == "":
                warnings.warn(Warnings.W108)
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

        DOCS: https://spacy.io/api/lemmatizer#is_base_form
        """
        return False

    def to_disk(
        self, path: Union[str, Path], *, exclude: Iterable[str] = SimpleFrozenList()
    ):
        """Serialize the pipe to disk.

        path (str / Path): Path to a directory.
        exclude (Iterable[str]): String names of serialization fields to exclude.

        DOCS: https://spacy.io/api/lemmatizer#to_disk
        """
        serialize = {}
        serialize["vocab"] = lambda p: self.vocab.to_disk(p, exclude=exclude)
        serialize["lookups"] = lambda p: self.lookups.to_disk(p)
        util.to_disk(path, serialize, exclude)

    def from_disk(
        self, path: Union[str, Path], *, exclude: Iterable[str] = SimpleFrozenList()
    ) -> "Lemmatizer":
        """Load the pipe from disk. Modifies the object in place and returns it.

        path (str / Path): Path to a directory.
        exclude (Iterable[str]): String names of serialization fields to exclude.
        RETURNS (Lemmatizer): The modified Lemmatizer object.

        DOCS: https://spacy.io/api/lemmatizer#from_disk
        """
        deserialize: Dict[str, Callable[[Any], Any]] = {}
        deserialize["vocab"] = lambda p: self.vocab.from_disk(p, exclude=exclude)
        deserialize["lookups"] = lambda p: self.lookups.from_disk(p)
        util.from_disk(path, deserialize, exclude)
        self._validate_tables()
        return self

    def to_bytes(self, *, exclude: Iterable[str] = SimpleFrozenList()) -> bytes:
        """Serialize the pipe to a bytestring.

        exclude (Iterable[str]): String names of serialization fields to exclude.
        RETURNS (bytes): The serialized object.

        DOCS: https://spacy.io/api/lemmatizer#to_bytes
        """
        serialize = {}
        serialize["vocab"] = lambda: self.vocab.to_bytes(exclude=exclude)
        serialize["lookups"] = self.lookups.to_bytes
        return util.to_bytes(serialize, exclude)

    def from_bytes(
        self, bytes_data: bytes, *, exclude: Iterable[str] = SimpleFrozenList()
    ) -> "Lemmatizer":
        """Load the pipe from a bytestring.

        bytes_data (bytes): The serialized pipe.
        exclude (Iterable[str]): String names of serialization fields to exclude.
        RETURNS (Lemmatizer): The loaded Lemmatizer.

        DOCS: https://spacy.io/api/lemmatizer#from_bytes
        """
        deserialize: Dict[str, Callable[[Any], Any]] = {}
        deserialize["vocab"] = lambda b: self.vocab.from_bytes(b, exclude=exclude)
        deserialize["lookups"] = lambda b: self.lookups.from_bytes(b)
        util.from_bytes(bytes_data, deserialize, exclude)
        self._validate_tables()
        return self


PUNCT_RULES = {"«": '"', "»": '"'}


class PyMorhpy2Lemmatizer(Lemmatizer):
    def __init__(
        self,
        vocab: Vocab,
        model: Optional[Model],
        lang: Literal["ru", "uk"],
        name: str = "lemmatizer",
        *,
        mode: str = "pymorphy2",
        overwrite: bool = False,
        scorer: Optional[Callable] = lemmatizer_score,
    ) -> None:
        if mode not in {"pymorphy2", "pymorphy2_lookup"}:
            raise ValueError(f"unknown mode for a pymorphy2 lemmatizer: {mode}")
        try:
            from pymorphy2 import MorphAnalyzer
        except ImportError:
            raise ImportError(
                "The Russian lemmatizer mode 'pymorphy2' requires the "
                "pymorphy2 library. Install it with: pip install pymorphy2"
            ) from None
        if getattr(self, "_morph", None) is None:
            self._morph = MorphAnalyzer(lang=lang)

        super().__init__(
            vocab, model, name, mode=mode, overwrite=overwrite, scorer=scorer
        )

    def pymorphy2_lemmatize(self, token: Token) -> List[str]:
        string = token.text
        univ_pos = token.pos_
        morphology = token.morph.to_dict()
        if univ_pos == "PUNCT":
            return [PUNCT_RULES.get(string, string)]
        if univ_pos not in ("ADJ", "DET", "NOUN", "NUM", "PRON", "PROPN", "VERB"):
            # Skip unchangeable pos
            return self.pymorphy2_lookup_lemmatize(token)
            return [string.lower()]
        analyses = self._morph.parse(string)
        filtered_analyses = []
        for analysis in analyses:
            if not analysis.is_known:
                # Skip suggested parse variant for unknown word for pymorphy
                continue
            analysis_pos, _ = oc2ud(str(analysis.tag))
            if analysis_pos == univ_pos or (
                analysis_pos in ("NOUN", "PROPN") and univ_pos in ("NOUN", "PROPN")
            ):
                filtered_analyses.append(analysis)
        if not len(filtered_analyses):
            return [string.lower()]
        if morphology is None or (len(morphology) == 1 and POS in morphology):
            return list(
                dict.fromkeys([analysis.normal_form for analysis in filtered_analyses])
            )
        if univ_pos in ("ADJ", "DET", "NOUN", "PROPN"):
            features_to_compare = ["Case", "Number", "Gender"]
        elif univ_pos == "NUM":
            features_to_compare = ["Case", "Gender"]
        elif univ_pos == "PRON":
            features_to_compare = ["Case", "Number", "Gender", "Person"]
        else:  # VERB
            features_to_compare = [
                "Aspect",
                "Gender",
                "Mood",
                "Number",
                "Tense",
                "VerbForm",
                "Voice",
            ]
        analyses, filtered_analyses = filtered_analyses, []
        for analysis in analyses:
            _, analysis_morph = oc2ud(str(analysis.tag))
            for feature in features_to_compare:
                if (
                    feature in morphology
                    and feature in analysis_morph
                    and morphology[feature].lower() != analysis_morph[feature].lower()
                ):
                    break
            else:
                filtered_analyses.append(analysis)
        if not len(filtered_analyses):
            return [string.lower()]
        return list(
            dict.fromkeys([analysis.normal_form for analysis in filtered_analyses])
        )

    def pymorphy2_lookup_lemmatize(self, token: Token) -> List[str]:
        string = token.text
        analyses = self._morph.parse(string)
        # often multiple forms would derive from the same normal form
        # thus check _unique_ normal forms
        normal_forms = set([an.normal_form for an in analyses])
        if len(normal_forms) == 1:
            return [next(iter(normal_forms))]
        return [string]


def oc2ud(oc_tag: str) -> Tuple[str, Dict[str, str]]:
    gram_map = {
        "_POS": {
            "ADJF": "ADJ",
            "ADJS": "ADJ",
            "ADVB": "ADV",
            "Apro": "DET",
            "COMP": "ADJ",  # Can also be an ADV - unchangeable
            "CONJ": "CCONJ",  # Can also be a SCONJ - both unchangeable ones
            "GRND": "VERB",
            "INFN": "VERB",
            "INTJ": "INTJ",
            "NOUN": "NOUN",
            "NPRO": "PRON",
            "NUMR": "NUM",
            "NUMB": "NUM",
            "PNCT": "PUNCT",
            "PRCL": "PART",
            "PREP": "ADP",
            "PRTF": "VERB",
            "PRTS": "VERB",
            "VERB": "VERB",
        },
        "Animacy": {"anim": "Anim", "inan": "Inan"},
        "Aspect": {"impf": "Imp", "perf": "Perf"},
        "Case": {
            "ablt": "Ins",
            "accs": "Acc",
            "datv": "Dat",
            "gen1": "Gen",
            "gen2": "Gen",
            "gent": "Gen",
            "loc2": "Loc",
            "loct": "Loc",
            "nomn": "Nom",
            "voct": "Voc",
        },
        "Degree": {"COMP": "Cmp", "Supr": "Sup"},
        "Gender": {"femn": "Fem", "masc": "Masc", "neut": "Neut"},
        "Mood": {"impr": "Imp", "indc": "Ind"},
        "Number": {"plur": "Plur", "sing": "Sing"},
        "NumForm": {"NUMB": "Digit"},
        "Person": {"1per": "1", "2per": "2", "3per": "3", "excl": "2", "incl": "1"},
        "Tense": {"futr": "Fut", "past": "Past", "pres": "Pres"},
        "Variant": {"ADJS": "Brev", "PRTS": "Brev"},
        "VerbForm": {
            "GRND": "Conv",
            "INFN": "Inf",
            "PRTF": "Part",
            "PRTS": "Part",
            "VERB": "Fin",
        },
        "Voice": {"actv": "Act", "pssv": "Pass"},
        "Abbr": {"Abbr": "Yes"},
    }
    pos = "X"
    morphology = dict()
    unmatched = set()
    grams = oc_tag.replace(" ", ",").split(",")
    for gram in grams:
        match = False
        for categ, gmap in sorted(gram_map.items()):
            if gram in gmap:
                match = True
                if categ == "_POS":
                    pos = gmap[gram]
                else:
                    morphology[categ] = gmap[gram]
        if not match:
            unmatched.add(gram)
    while len(unmatched) > 0:
        gram = unmatched.pop()
        if gram in ("Name", "Patr", "Surn", "Geox", "Orgn"):
            pos = "PROPN"
        elif gram == "Auxt":
            pos = "AUX"
        elif gram == "Pltm":
            morphology["Number"] = "Ptan"
    return pos, morphology

from typing import Optional, Callable, List, Dict

from .lookups import Lookups
from .parts_of_speech import NAMES as UPOS_NAMES


class Lemmatizer:
    """
    The Lemmatizer supports simple part-of-speech-sensitive suffix rules and
    lookup tables.

    DOCS: https://spacy.io/api/lemmatizer
    """

    def __init__(
        self,
        lookups: Optional[Lookups] = None,
        is_base_form: Optional[Callable] = None,
    ) -> None:
        """Initialize a Lemmatizer.

        lookups (Lookups): The lookups object containing the (optional) tables
            "lemma_rules", "lemma_index", "lemma_exc" and "lemma_lookup".
        RETURNS (Lemmatizer): The newly constructed object.
        """
        self.lookups = lookups if lookups is not None else Lookups()
        self.is_base_form = is_base_form

    def __call__(
        self, string: str, univ_pos: str, morphology: Optional[dict] = None
    ) -> List[str]:
        """Lemmatize a string.

        string (str): The string to lemmatize, e.g. the token text.
        univ_pos (str / int): The token's universal part-of-speech tag.
        morphology (dict): The token's morphological features following the
            Universal Dependencies scheme.
        RETURNS (list): The available lemmas for the string.
        """
        lookup_table = self.lookups.get_table("lemma_lookup", {})
        if "lemma_rules" not in self.lookups:
            return [lookup_table.get(string, string)]
        if isinstance(univ_pos, int):
            univ_pos = UPOS_NAMES.get(univ_pos, "X")
        univ_pos = univ_pos.lower()
        if univ_pos in ("", "eol", "space"):
            return [string.lower()]
        # See Issue #435 for example of where this logic is requied.
        if callable(self.is_base_form) and self.is_base_form(univ_pos, morphology):
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
        lemmas = self.lemmatize(
            string,
            index_table.get(univ_pos, {}),
            exc_table.get(univ_pos, {}),
            rules_table.get(univ_pos, []),
        )
        return lemmas

    def noun(self, string: str, morphology: Optional[dict] = None) -> List[str]:
        return self(string, "noun", morphology)

    def verb(self, string: str, morphology: Optional[dict] = None) -> List[str]:
        return self(string, "verb", morphology)

    def adj(self, string: str, morphology: Optional[dict] = None) -> List[str]:
        return self(string, "adj", morphology)

    def det(self, string: str, morphology: Optional[dict] = None) -> List[str]:
        return self(string, "det", morphology)

    def pron(self, string: str, morphology: Optional[dict] = None) -> List[str]:
        return self(string, "pron", morphology)

    def adp(self, string: str, morphology: Optional[dict] = None) -> List[str]:
        return self(string, "adp", morphology)

    def num(self, string: str, morphology: Optional[dict] = None) -> List[str]:
        return self(string, "num", morphology)

    def punct(self, string: str, morphology: Optional[dict] = None) -> List[str]:
        return self(string, "punct", morphology)

    def lookup(self, string: str, orth: Optional[int] = None) -> str:
        """Look up a lemma in the table, if available. If no lemma is found,
        the original string is returned.

        string (str): The original string.
        orth (int): Optional hash of the string to look up. If not set, the
            string will be used and hashed.
        RETURNS (str): The lemma if the string was found, otherwise the
            original string.
        """
        lookup_table = self.lookups.get_table("lemma_lookup", {})
        key = orth if orth is not None else string
        if key in lookup_table:
            return lookup_table[key]
        return string

    def lemmatize(
        self,
        string: str,
        index: Dict[str, List[str]],
        exceptions: Dict[str, Dict[str, List[str]]],
        rules: Dict[str, List[List[str]]],
    ) -> List[str]:
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

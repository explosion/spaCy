from typing import Dict, List, Tuple

from ...pipeline import Lemmatizer
from ...tokens import Token


class ItalianLemmatizer(Lemmatizer):
    """This lemmatizer was adapted from the Polish one (version of April 2021).
    It implements lookup lemmatization based on the morphological lexicon
    morph-it (Baroni and Zanchetta). The table lemma_lookup with non-POS-aware
    entries is used as a backup for words that aren't handled by morph-it."""

    @classmethod
    def get_lookups_config(cls, mode: str) -> Tuple[List[str], List[str]]:
        if mode == "pos_lookup":
            required = [
                "lemma_lookup_num",
                "lemma_lookup_det",
                "lemma_lookup_adp",
                "lemma_lookup_adj",
                "lemma_lookup_noun",
                "lemma_lookup_pron",
                "lemma_lookup_verb",
                "lemma_lookup_aux",
                "lemma_lookup_adv",
                "lemma_lookup_other",
                "lemma_lookup",
            ]
            return (required, [])
        else:
            return super().get_lookups_config(mode)

    def pos_lookup_lemmatize(self, token: Token) -> List[str]:
        string = token.text
        univ_pos = token.pos_
        morphology = token.morph.to_dict()
        lookup_pos = univ_pos.lower()
        if univ_pos == "PROPN":
            lookup_pos = "noun"
        elif univ_pos == "PART":
            lookup_pos = "pron"
        lookup_table = self.lookups.get_table("lemma_lookup_" + lookup_pos, {})
        if univ_pos == "NOUN":
            return self.lemmatize_noun(string, morphology, lookup_table)
        else:
            if univ_pos != "PROPN":
                string = string.lower()
            if univ_pos == "DET":
                return self.lemmatize_det(string, morphology, lookup_table)
            elif univ_pos == "PRON":
                return self.lemmatize_pron(string, morphology, lookup_table)
            elif univ_pos == "ADP":
                return self.lemmatize_adp(string, morphology, lookup_table)
            elif univ_pos == "ADJ":
                return self.lemmatize_adj(string, morphology, lookup_table)
            else:
                lemma = lookup_table.get(string, "")
        if not lemma:
            lookup_table = self.lookups.get_table("lemma_lookup_other")
            lemma = lookup_table.get(string, "")
        if not lemma:
            lookup_table = self.lookups.get_table(
                "lemma_lookup"
            )  # "legacy" lookup table
            lemma = lookup_table.get(string, string.lower())
        return [lemma]

    def lemmatize_det(
        self, string: str, morphology: dict, lookup_table: Dict[str, str]
    ) -> List[str]:
        if string in [
            "l'",
            "lo",
            "la",
            "i",
            "gli",
            "le",
        ]:
            return ["il"]
        if string in ["un'", "un", "una"]:
            return ["uno"]
        return [lookup_table.get(string, string)]

    def lemmatize_pron(
        self, string: str, morphology: dict, lookup_table: Dict[str, str]
    ) -> List[str]:
        if string in [
            "l'",
            "li",
            "la",
            "gli",
            "le",
        ]:
            return ["lo"]
        if string in ["un'", "un", "una"]:
            return ["uno"]
        lemma = lookup_table.get(string, string)
        if lemma == "alcun":
            lemma = "alcuno"
        elif lemma == "qualcun":
            lemma = "qualcuno"
        return [lemma]

    def lemmatize_adp(
        self, string: str, morphology: dict, lookup_table: Dict[str, str]
    ) -> List[str]:
        if string == "d'":
            return ["di"]
        return [lookup_table.get(string, string)]

    def lemmatize_adj(
        self, string: str, morphology: dict, lookup_table: Dict[str, str]
    ) -> List[str]:
        lemma = lookup_table.get(string, string)
        if lemma == "alcun":
            lemma = "alcuno"
        elif lemma == "qualcun":
            lemma = "qualcuno"
        return [lemma]

    def lemmatize_noun(
        self, string: str, morphology: dict, lookup_table: Dict[str, str]
    ) -> List[str]:
        # this method is case-sensitive, in order to work
        # for incorrectly tagged proper names
        if string != string.lower():
            if string.lower() in lookup_table:
                return [lookup_table[string.lower()]]
            elif string in lookup_table:
                return [lookup_table[string]]
            return [string.lower()]
        return [lookup_table.get(string, string)]

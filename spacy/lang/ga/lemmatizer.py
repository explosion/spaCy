from typing import List, Dict, Tuple

from ...pipeline import Lemmatizer
from ...tokens import Token
from .irish_morphology_helpers import unponc, demutate


class IrishLemmatizer(Lemmatizer):
    # This is a lookup-based lemmatiser using data extracted from
    # BuNaMo (https://github.com/michmech/BuNaMo)

    @classmethod
    def get_lookups_config(cls, mode: str) -> Tuple[List[str], List[str]]:
        if mode == "pos_lookup":
            # fmt: off
            required = [
                "lemma_lookup_adj", "lemma_lookup_adp",
                "lemma_lookup_noun", "lemma_lookup_verb"
            ]
            # fmt: on
            return (required, [])
        else:
            return super().get_lookups_config(mode)

    def pos_lookup_lemmatize(self, token: Token) -> List[str]:
        univ_pos = token.pos_
        string = unponc(token.text)
        if univ_pos not in ["PROPN", "ADP", "ADJ", "NOUN", "VERB"]:
            return [string.lower()]
        demutated = demutate(string)
        secondary = ""
        if string[0:1].lower() == "h" and string[1:2].lower() in "aáeéiíoóuú":
            secondary = string[1:]
        lookup_pos = univ_pos.lower()
        if univ_pos == "PROPN":
            lookup_pos = "noun"
        lookup_table = self.lookups.get_table("lemma_lookup_" + lookup_pos, {})

        def to_list(value):
            if value is None:
                value = []
            elif not isinstance(value, list):
                value = [value]
            return value

        if univ_pos == "ADP":
            return to_list(lookup_table.get(string, string.lower()))
        ret = []
        if univ_pos == "PROPN":
            ret.extend(to_list(lookup_table.get(demutated)))
            ret.extend(to_list(lookup_table.get(secondary)))
        else:
            ret.extend(to_list(lookup_table.get(demutated.lower())))
            ret.extend(to_list(lookup_table.get(secondary.lower())))
        if len(ret) == 0:
            ret = [string.lower()]
        return ret

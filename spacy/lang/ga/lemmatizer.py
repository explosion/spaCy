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
        morphology = token.morph.to_dict()
        lookup_pos = univ_pos.lower()
        try_orig = False
        if univ_pos == "PROPN":
            lookup_pos = "noun"
            try_orig = True
        lookup_table = self.lookups.get_table("lemma_lookup_" + lookup_pos, {})
        if univ_pos == "ADP":
            return [lookup_table.get(string, string.lower())]
        ret = []
        def addret(ret, input):
            if type(input) == list:
                ret += input
            elif type(input) == str:
                ret.append(input)
        if try_orig and demutated in lookup_table.keys():
            addret(ret, lookup_table.get(demutated))
        elif demutated.lower() in lookup_table.keys():
            addret(ret, lookup_table.get(demutated.lower()))
        if try_orig and secondary in lookup_table.keys():
            addret(ret, lookup_table.get(secondary))
        elif secondary.lower() in lookup_table.keys():
            addret(ret, lookup_table.get(secondary.lower()))
        if len(ret) == 0:
            return [string.lower()]
        else:
            return ret

from typing import List, Tuple

from ...lookups import Lookups
from ...pipeline import Lemmatizer
from ...tokens import Token


class HaitianCreoleLemmatizer(Lemmatizer):
    """
    Minimal Haitian Creole lemmatizer.
    Returns a word's base form based on rules and lookup,
    or defaults to the original form.
    """

    def is_base_form(self, token: Token) -> bool:
        morph = token.morph.to_dict()
        upos = token.pos_.lower()

        # Consider unmarked forms to be base
        if upos in {"noun", "verb", "adj", "adv"}:
            if not morph:
                return True
            if upos == "noun" and morph.get("Number") == "Sing":
                return True
            if upos == "verb" and morph.get("VerbForm") == "Inf":
                return True
            if upos == "adj" and morph.get("Degree") == "Pos":
                return True
        return False

    def rule_lemmatize(self, token: Token) -> List[str]:
        string = token.text.lower()
        pos = token.pos_.lower()
        cache_key = (token.orth, token.pos)
        if cache_key in self.cache:
            return self.cache[cache_key]

        forms = []

        # fallback rule: just return lowercased form
        forms.append(string)

        self.cache[cache_key] = forms
        return forms

    @classmethod
    def get_lookups_config(cls, mode: str) -> Tuple[List[str], List[str]]:
        if mode == "rule":
            required = ["lemma_lookup", "lemma_rules", "lemma_exc", "lemma_index"]
            return (required, [])
        return super().get_lookups_config(mode)

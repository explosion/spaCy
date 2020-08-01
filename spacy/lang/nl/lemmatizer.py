from typing import List, Optional

from thinc.api import Model

from ...lookups import Lookups
from ...pipeline import Lemmatizer
from ...tokens import Token
from ...vocab import Vocab


class DutchLemmatizer(Lemmatizer):
    def __init__(
        self,
        vocab: Vocab,
        model: Optional[Model],
        name: str = "lemmatizer",
        *,
        mode: str = "rule",
        lookups: Optional[Lookups] = None,
    ) -> None:
        super().__init__(vocab, model, name, mode=mode, lookups=lookups)
        self.cache_features["rule"] = ["LOWER", "POS"]

    # Note: CGN does not distinguish AUX verbs, so we treat AUX as VERB.
    def rule_lemmatize(self, token: Token) -> List[str]:
        # Difference 1: self.rules is assumed to be non-None, so no
        # 'is None' check required.
        # String lowercased from the get-go. All lemmatization results in
        # lowercased strings. For most applications, this shouldn't pose
        # any problems, and it keeps the exceptions indexes small. If this
        # creates problems for proper nouns, we can introduce a check for
        # univ_pos == "PROPN".
        string = token.text
        univ_pos = token.pos_.lower()
        if univ_pos in ("", "eol", "space"):
            return [string.lower()]

        index_table = self.lookups.get_table("lemma_index", {})
        exc_table = self.lookups.get_table("lemma_exc", {})
        rules_table = self.lookups.get_table("lemma_rules", {})
        index = index_table.get(univ_pos, {})
        exceptions = exc_table.get(univ_pos, {})
        rules = rules_table.get(univ_pos, {})

        string = string.lower()
        if univ_pos not in ("noun", "verb", "aux", "adj", "adv", "pron", "det", "adp", "num"):
            return [string]
        lemma_index = index_table.get(univ_pos, {})
        # string is already lemma
        if string in lemma_index:
            return [string]
        exc_table = self.lookups.get_table("lemma_exc", {})
        exceptions = exc_table.get(univ_pos, {})
        # string is irregular token contained in exceptions index.
        try:
            lemma = exceptions[string]
            return [lemma[0]]
        except KeyError:
            pass
        # string corresponds to key in lookup table
        lookup_table = self.lookups.get_table("lemma_lookup", {})
        looked_up_lemma = lookup_table.get(string)
        if looked_up_lemma and looked_up_lemma in lemma_index:
            return [looked_up_lemma]
        rules_table = self.lookups.get_table("lemma_rules", {})
        oov_forms = []
        for old, new in rules:
            if string.endswith(old):
                form = string[: len(string) - len(old)] + new
                if not form:
                    pass
                elif form in index:
                    return [form]
                else:
                    oov_forms.append(form)
        forms = list(set(oov_forms))
        # Back-off through remaining return value candidates.
        if forms:
            for form in forms:
                if form in exceptions:
                    return [form]
            if looked_up_lemma:
                return [looked_up_lemma]
            else:
                return forms
        elif looked_up_lemma:
            return [looked_up_lemma]
        else:
            return [string]

    def lookup_lemmatize(self, token: Token) -> List[str]:
        """Overrides parent method so that a lowercased version of the string
        is used to search the lookup table. This is necessary because our
        lookup table consists entirely of lowercase keys."""
        lookup_table = self.lookups.get_table("lemma_lookup", {})
        string = token.text.lower()
        return [lookup_table.get(string, string)]

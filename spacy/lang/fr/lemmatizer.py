from typing import List

from ...parts_of_speech import NAMES as UPOS_NAMES
from ...pipeline import Lemmatizer
from ...tokens import Token


class FrenchLemmatizer(Lemmatizer):
    """
    French language lemmatizer applies the default rule based lemmatization
    procedure with some modifications for better French language support.

    The parts of speech 'ADV', 'PRON', 'DET', 'ADP' and 'AUX' are added to use
    the rule-based lemmatization. As a last resort, the lemmatizer checks in
    the lookup table.
    """

    def rule_lemmatize(self, token: Token) -> List[str]:
        string = token.text
        univ_pos = token.pos_
        if isinstance(univ_pos, int):
            univ_pos = UPOS_NAMES.get(univ_pos, "X")
        univ_pos = univ_pos.lower()
        if univ_pos in ("", "eol", "space"):
            return [string.lower()]
        elif "lemma_rules" not in self.lookups or univ_pos not in (
            "noun",
            "verb",
            "adj",
            "adp",
            "adv",
            "aux",
            "cconj",
            "det",
            "pron",
            "punct",
            "sconj",
        ):
            return self.lookup_lemmatize(token)
        index_table = self.lookups.get_table("lemma_index", {})
        exc_table = self.lookups.get_table("lemma_exc", {})
        rules_table = self.lookups.get_table("lemma_rules", {})
        lookup_table = self.lookups.get_table("lemma_lookup", {})
        index = index_table.get(univ_pos, {})
        exceptions = exc_table.get(univ_pos, {})
        rules = rules_table.get(univ_pos, [])
        string = string.lower()
        forms = []
        if string in index:
            forms.append(string)
            return forms
        forms.extend(exceptions.get(string, []))
        oov_forms = []
        if not forms:
            for old, new in rules:
                if string.endswith(old):
                    form = string[: len(string) - len(old)] + new
                    if not form:
                        pass
                    elif form in index or not form.isalpha():
                        forms.append(form)
                    else:
                        oov_forms.append(form)
        if not forms:
            forms.extend(oov_forms)
        if not forms and string in lookup_table.keys():
            forms.append(self.lookup_lemmatize(token)[0])
        if not forms:
            forms.append(string)
        return list(set(forms))

import re
from typing import Callable, List, Optional, Union

import pydantic
from pydantic import BaseModel

if pydantic.VERSION.split(".")[0] == "1":  # type: ignore
    from pydantic import validator  # type: ignore
else:
    from pydantic import field_validator as validator  # type: ignore

from ..language import Language
from ..tokens import Doc, Token
from ..vocab import Vocab
from .pipe import Pipe

######### helper functions across the default splitting rules ##############


def _split_doc(doc: Doc) -> bool:
    """Check to see if the document has a noun phrase
        with a modifier and a conjunction.

    Args:
        doc (Doc): The input document.

    Returns:
        bool: True if the document has a noun phrase
            with a modifier and a conjunction, else False.
    """

    noun_modified = False
    has_conjunction = False

    for token in doc:
        if token.head.pos_ == "NOUN":  ## check to see that the phrase is a noun phrase
            for child in token.head.children:
                if child.dep_ in ["amod", "advmod", "nmod"]:
                    noun_modified = True

        # check if there is a conjunction in the phrase
        if token.pos_ == "CCONJ":
            has_conjunction = True

    if noun_modified and has_conjunction:
        return True

    else:
        return False


def _collect_modifiers(token: Token) -> List[str]:
    """Collects adverbial modifiers for a given token.

    Args:
        token (Token): The input token.

    Returns:
        List[str]: A list of modifiers for the token.
    """
    modifiers = []
    for child in token.children:
        if child.dep_ == "amod":
            # collect adverbial modifiers for this adjective
            adv_mods = [
                adv_mod.text
                for adv_mod in child.children
                if adv_mod.dep_ in ["advmod"] and not adv_mod.pos_ == "CCONJ"
            ]

            modifier_phrase = " ".join(adv_mods + [child.text])
            modifiers.append(modifier_phrase)
            # also check for conjunctions to this adjective
            for conj in child.conjuncts:
                adv_mods_conj = [
                    adv_mod.text
                    for adv_mod in conj.children
                    if adv_mod.dep_ in ["advmod"] and not adv_mod.pos_ == "CCONJ"
                ]
                modifier_phrase_conj = " ".join(adv_mods_conj + [conj.text])
                modifiers.append(modifier_phrase_conj)

    return modifiers


########### DEFAULT COORDINATION SPLITTING RULES ##############


def split_noun_coordination(doc: Doc) -> Union[List[str], None]:
    """Identifies and splits noun phrases with a modifier
        and a conjunction.

    construction cases:
        - "apples and oranges" -> None
        - "green apples and oranges" -> ["green apples", "green oranges"]
        - "apples and juicy oranges" -> ["juicy apples", "juicy oranges"]
        - "hot chicken wings and soup" -> ["hot chicken wings", "hot soup"]
        - "green apples and rotten oranges" -> ["green apples", "rotten oranges"]
        - "very green apples and oranges" -> ["very green apples", "very green oranges"]
        - "delicious and juicy apples" -> ["delicious apples", "juicy apples"]
        - "delicious but quite sour apples" -> ["delicious apples", "quite sour apples"]
        - "delicious but quite sour apples and oranges" -> ["delicious apples", "quite sour apples", "delicious oranges", "quite sour oranges"]

    Args:
        doc (Doc): The input document.

    Returns:
        Union[List[str], None]: A list of the coordinated noun phrases,
            or None if no coordinated noun phrases are found.
    """
    phrases = []
    modified_nouns = set()
    to_split = _split_doc(doc)

    if to_split:
        for token in doc:
            if token.dep_ == "amod" and token.head.pos_ == "NOUN":
                head_noun = token.head

                if head_noun not in modified_nouns:
                    modifier_phrases = _collect_modifiers(head_noun)
                    nouns_to_modify = [head_noun] + list(head_noun.conjuncts)

                    for noun in nouns_to_modify:
                        compound_parts = [
                            child.text
                            for child in noun.lefts
                            if child.dep_ == "compound"
                        ]
                        complete_noun_phrase = " ".join(compound_parts + [noun.text])
                        for modifier_phrase in modifier_phrases:
                            phrases.append(f"{modifier_phrase} {complete_noun_phrase}")
                        modified_nouns.add(noun)  # mark this noun as modified

        return phrases if phrases != [] else None
    else:
        return None


###############################################################


class SplittingRule(BaseModel):
    function: Callable[[Doc], Union[List[str], None]]

    @validator("function")
    def check_return_type(cls, v):
        dummy_doc = Doc(Language().vocab, words=["dummy", "doc"], spaces=[True, False])
        result = v(dummy_doc)
        if result is not None:
            if not isinstance(result, List):
                raise ValueError(
                    "The custom splitting rule must return None or a list."
                )
            elif not all(isinstance(item, str) for item in result):
                raise ValueError(
                    "The custom splitting rule must return None or a list of strings."
                )
        return v


@Language.factory(
    "coordination_splitter", requires=["token.dep", "token.tag", "token.pos"]
)
def make_coordination_splitter(nlp: Language, name: str):
    """Make a CoordinationSplitter component.

    the default splitting rules include:
        - split_noun_coordination

    Args:
        nlp (Language): The spaCy Language object.
        name (str): The name of the component.

    RETURNS The CoordinationSplitter component.

    DOCS: xxx
    """

    return CoordinationSplitter(nlp.vocab, name=name)


class CoordinationSplitter(Pipe):
    def __init__(
        self,
        vocab: Vocab,
        name: str = "coordination_splitter",
        rules: Optional[List[SplittingRule]] = None,
    ) -> None:
        self.name = name
        self.vocab = vocab
        if rules is None:
            default_rules = [
                split_noun_coordination,
            ]
            self.rules = [SplittingRule(function=rule) for rule in default_rules]
        else:
            self.rules = [
                rule
                if isinstance(rule, SplittingRule)
                else SplittingRule(function=rule)
                for rule in rules
            ]

    def clear_rules(self) -> None:
        """Clear the default splitting rules."""
        self.rules = []

    def add_default_rules(self) -> None:
        """Reset the default splitting rules."""
        default_rules = [
            split_noun_coordination,
        ]
        self.rules = [SplittingRule(function=rule) for rule in default_rules]

    def add_rule(self, rule: Callable[[Doc], Union[List[str], None]]) -> None:
        """Add a single splitting rule to the default rules."""
        validated_rule = SplittingRule(function=rule)
        self.rules.append(validated_rule)

    def add_rules(self, rules: List[Callable[[Doc], Union[List[str], None]]]) -> None:
        """Add a list of splitting rules to the default rules.

        Args:
            rules (List[Callable[[Doc], Union[List[str], None]]]): A list of functions to be added as splitting rules.
        """
        for rule in rules:
            # Wrap each rule in a SplittingRule instance to ensure it's validated
            validated_rule = SplittingRule(function=rule)
            self.rules.append(validated_rule)

    def __call__(self, doc: Doc) -> Doc:
        """Apply the splitting rules to the doc.

        Args:
            doc (Doc): The spaCy Doc object.

        Returns:
            Doc: The modified spaCy Doc object.
        """
        if doc.lang_ != "en":
            return doc

        for rule in self.rules:
            split = rule.function(doc)
            if split:
                return Doc(doc.vocab, words=split)
        return doc

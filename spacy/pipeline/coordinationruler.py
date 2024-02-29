from typing import List, Callable, Optional, Union
from pydantic import BaseModel, validator
import re

from ..tokens import Doc
from ..language import Language
from ..vocab import Vocab
from .pipe import Pipe

########### DEFAULT COORDINATION SPLITTING RULES ##############
 
def split_noun_coordination(doc: Doc) -> Union[List[str], None]:
    """Identifies and splits phrases with multiple nouns, a modifier
        and a conjunction.
    
    Examples:
        - "apples and oranges" -> None
        - "green apples and oranges" -> ["green apples", "green oranges"]
        - "green apples and rotten oranges" -> None
        - "apples and juicy oranges" -> ["juicy apples", "juicy oranges"]
        - "hot chicken wings and soup" -> ["hot chicken wings", "hot soup"]
        - "spicy ice cream and chicken wings" -> ["spicy ice cream", "spicy chicken wings"]
    
    Args:
        doc (Doc): The input document.

    Returns:
        Union[List[str], None]: A list of the coordinated noun phrases, 
            or None if no coordinated noun phrases are found.
    """
    def _split_doc(doc: Doc) -> bool:
        noun_modified = False
        has_conjunction = False
        
        for token in doc:
            if token.head.pos_ == 'NOUN': ## check to see that the phrase is a noun phrase
                has_modifier = any(child.dep_ == 'amod' for child in token.head.children) #check to see if the noun has a modifier
                if has_modifier:
                    noun_modified = True
            # check if there is a conjunction linked directly to a noun
            if token.dep_ == 'conj' and token.head.pos_ == 'NOUN':
                has_conjunction = True
        
        return True if noun_modified and has_conjunction else False
    
    phrases = []
    modified_nouns = set()  
    to_split = _split_doc(doc)
    
    if to_split: 
        for token in doc:
            if token.dep_ == "amod" and token.head.pos_ == "NOUN":
                modifier = token.text
                head_noun = token.head
                
                if head_noun not in modified_nouns:
                    nouns_to_modify = [head_noun] + list(head_noun.conjuncts)
                                        
                    for noun in nouns_to_modify:
                        compound_parts = [child.text for child in noun.lefts if child.dep_ == "compound"]
                        complete_noun_phrase = " ".join(compound_parts + [noun.text])        
                        phrases.append(f"{modifier} {complete_noun_phrase}")
                        modified_nouns.add(noun)  # Mark this noun as modified

        return phrases if phrases != [] else None
    else:
        return None


###############################################################

# class SplittingRule(BaseModel):
#     function: Callable[[Doc], Union[List[str], None]]

#     @validator("function")
#     def check_return_type(cls, v):
#         nlp = en_core_web_sm.load()
#         dummy_doc = nlp("This is a dummy sentence.")
#         result = v(dummy_doc)
#         if result is not None:
#             if not isinstance(result, List):
#                 raise ValueError(
#                     "The custom splitting rule must return None or a list."
#                 )
#             elif not all(isinstance(item, str) for item in result):
#                 raise ValueError(
#                     "The custom splitting rule must return None or a list of strings."
#                 )
#         return v


# @Language.factory(
#     "coordination_splitter", requires=["token.dep", "token.tag", "token.pos"]
# )
# def make_coordination_splitter(nlp: Language, name: str):
#     """Make a CoordinationSplitter component.

#     the default splitting rules include:

#     - _split_duplicate_object: Split a text with 2 verbs and 1 object (and optionally a subject) into two texts each with 1 verb, the shared object (and its modifiers), and the subject if present.
#     - _split_duplicate_verb: Split a text with 1 verb and 2 objects into two texts each with 1 verb and 1 object.
#     - _split_skill_mentions: Split a text with 2 skills into 2 texts with 1 skill (the phrase must end with 'skills' and the skills must be separated by 'and')


#     Args:
#         nlp (Language): The spaCy Language object.
#         name (str): The name of the component.

#     RETURNS The CoordinationSplitter component.

#     DOCS: xxx
#     """

#     return CoordinationSplitter(nlp.vocab, name=name)


# class CoordinationSplitter(Pipe):
#     def __init__(
#         self,
#         vocab: Vocab,
#         name: str = "coordination_splitter",
#         rules: Optional[List[SplittingRule]] = None,
#     ) -> None:
#         self.name = name
#         self.vocab = vocab
#         if rules is None:
#             default_rules = [
#                 _split_duplicate_object,
#                 _split_duplicate_verb,
#                 _split_skill_mentions,
#             ]
#             self.rules = [SplittingRule(function=rule) for rule in default_rules]
#         else:
#             # Ensure provided rules are wrapped in SplittingRule instances
#             self.rules = [
#                 rule
#                 if isinstance(rule, SplittingRule)
#                 else SplittingRule(function=rule)
#                 for rule in rules
#             ]

#     def clear_rules(self) -> None:
#         """Clear the default splitting rules."""
#         self.rules = []

#     def add_default_rules(self) -> List[SplittingRule]:
#         """Reset the default splitting rules."""
#         default_rules = [
#             _split_duplicate_object,
#             _split_duplicate_verb,
#             _split_skill_mentions,
#         ]
#         self.rules = [SplittingRule(function=rule) for rule in default_rules]

#     def add_rule(self, rule: Callable[[Doc], Union[List[str], None]]) -> None:
#         """Add a single splitting rule to the default rules."""
#         validated_rule = SplittingRule(function=rule)
#         self.rules.append(validated_rule)

#     def add_rules(self, rules: List[Callable[[Doc], Union[List[str], None]]]) -> None:
#         """Add a list of splitting rules to the default rules.

#         Args:
#             rules (List[Callable[[Doc], Union[List[str], None]]]): A list of functions to be added as splitting rules.
#         """
#         for rule in rules:
#             # Wrap each rule in a SplittingRule instance to ensure it's validated
#             validated_rule = SplittingRule(function=rule)
#             self.rules.append(validated_rule)

#     def __call__(self, doc: Doc) -> Doc:
#         """Apply the splitting rules to the doc.

#         Args:
#             doc (Doc): The spaCy Doc object.

#         Returns:
#             Doc: The modified spaCy Doc object.
#         """
#         if doc.lang_ != "en":
#             return doc

#         for rule in self.rules:
#             split = rule.function(doc)
#             if split:
#                 return Doc(doc.vocab, words=split)
#         return doc

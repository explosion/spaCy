from typing import List, Callable, Optional, Union
from pydantic import BaseModel, validator
import re
import en_core_web_sm

from ..tokens import Doc
from ..language import Language
from ..vocab import Vocab
from .pipe import Pipe

########### DEFAULT COORDINATION SPLITTING RULES ##############


def _split_duplicate_object(doc: Doc) -> Union[List[str], None]:
    """Split a text with 2 verbs and 1 object (and optionally a subject) into
       2 texts each with 1 verb, the shared object (and its modifiers), and the subject if present.

    i.e. 'I use and provide clinical supervision' -->
    ['I use clinical supervision', 'I provide clinical supervision']

    Args:
        doc (Doc): The spaCy Doc object.

    Returns:
        List[str]: The split texts.
    """
    sentences = []

    for token in doc:
        if token.pos_ == "VERB" and (token.dep_ == "ROOT" or token.dep_ == "conj"):

            has_AND = False
            has_second_verb = False
            has_dobj = False
            subject = None

            # Find the subject if it exists
            for possible_subject in token.head.children:
                if possible_subject.dep_ in ["nsubj", "nsubjpass"]:
                    subject = possible_subject
                    break

            for child in token.children:

                if child.pos_ == "CCONJ" and child.lemma_ == "and":
                    has_AND = True

                if child.pos_ == "VERB" and child.dep_ == "conj":
                    has_second_verb = True
                    second_verb = child
                    first_verb = token.head if token.dep_ == "conj" else token

                    for descendant in second_verb.subtree:
                        if descendant.dep_ == "dobj":
                            has_dobj = True
                            # Collect the full noun phrase for the direct object
                            dobj_span = doc[
                                descendant.left_edge.i : descendant.right_edge.i + 1
                            ]
                            dobj = dobj_span.text

            if has_AND and has_second_verb and has_dobj:
                subject_text = subject.text + " " if subject else ""
                first_text = "{}{} {}".format(subject_text, first_verb, dobj)
                second_text = "{}{} {}".format(subject_text, second_verb, dobj)

                sentences.extend([first_text, second_text])

    return sentences if sentences else None


def _split_on_and(text: str) -> List[str]:
    """Split a text on 'and' and return a list of the split texts.

    Args:
        text (str): The text to split.

    Returns:
        List[str]: The split texts.
    """
    text = re.sub(r"\s\s+", " ", text)

    replacements = {
        ";": ",",
        ", and ,": " and ",
        ", and,": " and ",
        ",and ,": " and ",
        ", and ": " and ",
        " and ,": " and ",
        ",and,": " and ",
        " and,": " and ",
        ",and ": " and ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    return [t.strip() for t in re.split(r",| and ", text)]


def _split_duplicate_verb(doc: Doc) -> Union[List[str], None]:
    """Split a text with 1 verb and 2 objects.

    i.e. 'I love using smartphones and apps' -->
    ['I love using smartphones', 'I love using apps']

    Args:
        doc (Doc): The spaCy Doc object.

    Returns:
        List[str]: The split texts.
    """

    for token in doc:

        if token.pos_ == "VERB" and token.dep_ == "ROOT":

            has_AND = False
            has_dobj = False
            has_sec_obj = False
            subject = ""

            for child in token.children:

                if child.dep_ == "dobj":
                    has_dobj = True

                subject = child.text if child.dep_ == "nsubj" else subject

                objects = " ".join(
                    [
                        c.text
                        for c in token.subtree
                        if c.text != token.text and c.dep_ != "nsubj"
                    ]
                )

                split_objects = _split_on_and(objects)

                object_list = []
                for split in split_objects:
                    object_list.append(split)

                for subchild in child.children:

                    if subchild.pos_ == "CCONJ" and subchild.lemma_ == "and":
                        has_AND = True

                    if subchild.dep_ == "conj":
                        has_sec_obj = True

                if has_AND and has_dobj and has_sec_obj:
                    text_list = [
                        f"{subject} {token.text} {split}.".strip()
                        for split in object_list
                    ]
                    return [text.replace(" ..", ".") for text in text_list]

    return None


def _split_skill_mentions(doc: Doc) -> Union[List[str], None]:
    """Split a text with 2 skills into 2 texts with 1 skill.

        i.e. 'written and oral communication skills' -->
    ['written communication skills', 'oral communication skills']

    Args:
        text (str): The text to split.

    Returns:
        List[str]: The split texts.
    """
    for token in doc:
        if (
            token.pos_ == "NOUN"
            and token.lemma_ == "skill"
            and token.idx == doc[-1].idx
        ):

            has_AND = False

            root = [token for token in doc if token.dep_ == "ROOT"]
            if root:
                root = root[0]

                for child in root.subtree:

                    if child.pos_ == "CCONJ" and child.lemma_ == "and":
                        has_AND = True

                if has_AND:
                    skill_def = " ".join(
                        [c.text for c in root.subtree if c.text != token.text]
                    )

                    split_skills = _split_on_and(skill_def)

                    skill_lists = []
                    for split_skill in split_skills:
                        skill_lists.append("{} {}".format(split_skill, token.text))

                    return skill_lists
    return None


class SplittingRule(BaseModel):
    function: Callable[[Doc], Union[List[str], None]]

    @validator("function")
    def check_return_type(cls, v):
        nlp = en_core_web_sm.load()
        dummy_doc = nlp("This is a dummy sentence.")
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

    - _split_duplicate_object: Split a text with 2 verbs and 1 object (and optionally a subject) into two texts each with 1 verb, the shared object (and its modifiers), and the subject if present.
    - _split_duplicate_verb: Split a text with 1 verb and 2 objects into two texts each with 1 verb and 1 object.
    - _split_skill_mentions: Split a text with 2 skills into 2 texts with 1 skill (the phrase must end with 'skills' and the skills must be separated by 'and')


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
                _split_duplicate_object,
                _split_duplicate_verb,
                _split_skill_mentions,
            ]
            self.rules = [SplittingRule(function=rule) for rule in default_rules]
        else:
            # Ensure provided rules are wrapped in SplittingRule instances
            self.rules = [
                rule
                if isinstance(rule, SplittingRule)
                else SplittingRule(function=rule)
                for rule in rules
            ]

    def clear_rules(self) -> None:
        """Clear the default splitting rules."""
        self.rules = []

    def add_default_rules(self) -> List[SplittingRule]:
        """Reset the default splitting rules."""
        default_rules = [
            _split_duplicate_object,
            _split_duplicate_verb,
            _split_skill_mentions,
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

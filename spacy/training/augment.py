from typing import Callable, Iterator, Dict, List, Tuple, TYPE_CHECKING
import random
import itertools
from functools import partial
from pydantic import BaseModel, StrictStr

from ..util import registry
from .example import Example

if TYPE_CHECKING:
    from ..language import Language  # noqa: F401


class OrthVariantsSingle(BaseModel):
    tags: List[StrictStr]
    variants: List[StrictStr]


class OrthVariantsPaired(BaseModel):
    tags: List[StrictStr]
    variants: List[List[StrictStr]]


class OrthVariants(BaseModel):
    paired: List[OrthVariantsPaired] = []
    single: List[OrthVariantsSingle] = []


@registry.augmenters("spacy.orth_variants.v1")
def create_orth_variants_augmenter(
    level: float, lower: float, orth_variants: OrthVariants
) -> Callable[["Language", Example], Iterator[Example]]:
    """Create a data augmentation callback that uses orth-variant replacement.
    The callback can be added to a corpus or other data iterator during training.

    level (float): The percentage of texts that will be augmented.
    lower (float): The percentage of texts that will be lowercased.
    orth_variants (Dict[str, dict]): A dictionary containing the single and
        paired orth variants. Typically loaded from a JSON file.
    RETURNS (Callable[[Language, Example], Iterator[Example]]): The augmenter.
    """
    return partial(
        orth_variants_augmenter, orth_variants=orth_variants, level=level, lower=lower
    )


@registry.augmenters("spacy.lower_case.v1")
def create_lower_casing_augmenter(
    level: float,
) -> Callable[["Language", Example], Iterator[Example]]:
    """Create a data augmentation callback that converts documents to lowercase.
    The callback can be added to a corpus or other data iterator during training.

    level (float): The percentage of texts that will be augmented.
    RETURNS (Callable[[Language, Example], Iterator[Example]]): The augmenter.
    """
    return partial(lower_casing_augmenter, level=level)


def dont_augment(nlp: "Language", example: Example) -> Iterator[Example]:
    yield example


def lower_casing_augmenter(
    nlp: "Language", example: Example, *, level: float
) -> Iterator[Example]:
    if random.random() >= level:
        yield example
    else:
        example_dict = example.to_dict()
        doc = nlp.make_doc(example.text.lower())
        example_dict["token_annotation"]["ORTH"] = [t.lower_ for t in example.reference]
        yield example.from_dict(doc, example_dict)


def orth_variants_augmenter(
    nlp: "Language",
    example: Example,
    orth_variants: Dict,
    *,
    level: float = 0.0,
    lower: float = 0.0,
) -> Iterator[Example]:
    if random.random() >= level:
        yield example
    else:
        raw_text = example.text
        orig_dict = example.to_dict()
        variant_text, variant_token_annot = make_orth_variants(
            nlp,
            raw_text,
            orig_dict["token_annotation"],
            orth_variants,
            lower=raw_text is not None and random.random() < lower,
        )
        orig_dict["token_annotation"] = variant_token_annot
        yield example.from_dict(nlp.make_doc(variant_text), orig_dict)


def make_orth_variants(
    nlp: "Language",
    raw: str,
    token_dict: Dict[str, List[str]],
    orth_variants: Dict[str, List[Dict[str, List[str]]]],
    *,
    lower: bool = False,
) -> Tuple[str, Dict[str, List[str]]]:
    words = token_dict.get("ORTH", [])
    tags = token_dict.get("TAG", [])
    # keep unmodified if words are not defined
    if not words:
        return raw, token_dict
    if lower:
        words = [w.lower() for w in words]
        raw = raw.lower()
    # if no tags, only lowercase
    if not tags:
        token_dict["ORTH"] = words
        return raw, token_dict
    # single variants
    ndsv = orth_variants.get("single", [])
    punct_choices = [random.choice(x["variants"]) for x in ndsv]
    for word_idx in range(len(words)):
        for punct_idx in range(len(ndsv)):
            if (
                tags[word_idx] in ndsv[punct_idx]["tags"]
                and words[word_idx] in ndsv[punct_idx]["variants"]
            ):
                words[word_idx] = punct_choices[punct_idx]
    # paired variants
    ndpv = orth_variants.get("paired", [])
    punct_choices = [random.choice(x["variants"]) for x in ndpv]
    for word_idx in range(len(words)):
        for punct_idx in range(len(ndpv)):
            if tags[word_idx] in ndpv[punct_idx]["tags"] and words[
                word_idx
            ] in itertools.chain.from_iterable(ndpv[punct_idx]["variants"]):
                # backup option: random left vs. right from pair
                pair_idx = random.choice([0, 1])
                # best option: rely on paired POS tags like `` / ''
                if len(ndpv[punct_idx]["tags"]) == 2:
                    pair_idx = ndpv[punct_idx]["tags"].index(tags[word_idx])
                # next best option: rely on position in variants
                # (may not be unambiguous, so order of variants matters)
                else:
                    for pair in ndpv[punct_idx]["variants"]:
                        if words[word_idx] in pair:
                            pair_idx = pair.index(words[word_idx])
                words[word_idx] = punct_choices[punct_idx][pair_idx]
    token_dict["ORTH"] = words
    # construct modified raw text from words and spaces
    raw = ""
    for orth, spacy in zip(token_dict["ORTH"], token_dict["SPACY"]):
        raw += orth
        if spacy:
            raw += " "
    return raw, token_dict

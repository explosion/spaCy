import itertools
import random
from functools import partial
from typing import TYPE_CHECKING, Callable, Dict, Iterator, List, Optional, Tuple

from ..util import registry
from .example import Example
from .iob_utils import _doc_to_biluo_tags_with_partial, split_bilu_label

if TYPE_CHECKING:
    from ..language import Language  # noqa: F401


@registry.augmenters("spacy.combined_augmenter.v1")
def create_combined_augmenter(
    lower_level: float,
    orth_level: float,
    orth_variants: Optional[Dict[str, List[Dict]]],
    whitespace_level: float,
    whitespace_per_token: float,
    whitespace_variants: Optional[List[str]],
) -> Callable[["Language", Example], Iterator[Example]]:
    """Create a data augmentation callback that uses orth-variant replacement.
    The callback can be added to a corpus or other data iterator during training.

    lower_level (float): The percentage of texts that will be lowercased.
    orth_level (float): The percentage of texts that will be augmented.
    orth_variants (Optional[Dict[str, List[Dict]]]): A dictionary containing the
        single and paired orth variants. Typically loaded from a JSON file.
    whitespace_level (float): The percentage of texts that will have whitespace
        tokens inserted.
    whitespace_per_token (float): The number of whitespace tokens to insert in
        the modified doc as a percentage of the doc length.
    whitespace_variants (Optional[List[str]]): The whitespace token texts.
    RETURNS (Callable[[Language, Example], Iterator[Example]]): The augmenter.
    """
    return partial(
        combined_augmenter,
        lower_level=lower_level,
        orth_level=orth_level,
        orth_variants=orth_variants,
        whitespace_level=whitespace_level,
        whitespace_per_token=whitespace_per_token,
        whitespace_variants=whitespace_variants,
    )


def combined_augmenter(
    nlp: "Language",
    example: Example,
    *,
    lower_level: float = 0.0,
    orth_level: float = 0.0,
    orth_variants: Optional[Dict[str, List[Dict]]] = None,
    whitespace_level: float = 0.0,
    whitespace_per_token: float = 0.0,
    whitespace_variants: Optional[List[str]] = None,
) -> Iterator[Example]:
    if random.random() < lower_level:
        example = make_lowercase_variant(nlp, example)
    if orth_variants and random.random() < orth_level:
        raw_text = example.text
        orig_dict = example.to_dict()
        orig_dict["doc_annotation"]["entities"] = _doc_to_biluo_tags_with_partial(
            example.reference
        )
        variant_text, variant_token_annot = make_orth_variants(
            nlp,
            raw_text,
            orig_dict["token_annotation"],
            orth_variants,
            lower=False,
        )
        orig_dict["token_annotation"] = variant_token_annot
        example = example.from_dict(nlp.make_doc(variant_text), orig_dict)
    if whitespace_variants and random.random() < whitespace_level:
        for _ in range(int(len(example.reference) * whitespace_per_token)):
            example = make_whitespace_variant(
                nlp,
                example,
                random.choice(whitespace_variants),
                random.randrange(0, len(example.reference)),
            )
    yield example


@registry.augmenters("spacy.orth_variants.v1")
def create_orth_variants_augmenter(
    level: float, lower: float, orth_variants: Dict[str, List[Dict]]
) -> Callable[["Language", Example], Iterator[Example]]:
    """Create a data augmentation callback that uses orth-variant replacement.
    The callback can be added to a corpus or other data iterator during training.

    level (float): The percentage of texts that will be augmented.
    lower (float): The percentage of texts that will be lowercased.
    orth_variants (Dict[str, List[Dict]]): A dictionary containing
        the single and paired orth variants. Typically loaded from a JSON file.
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
        yield make_lowercase_variant(nlp, example)


def make_lowercase_variant(nlp: "Language", example: Example):
    example_dict = example.to_dict()
    example_dict["doc_annotation"]["entities"] = _doc_to_biluo_tags_with_partial(
        example.reference
    )
    doc = nlp.make_doc(example.text.lower())
    example_dict["token_annotation"]["ORTH"] = [t.lower_ for t in example.reference]
    return example.from_dict(doc, example_dict)


def orth_variants_augmenter(
    nlp: "Language",
    example: Example,
    orth_variants: Dict[str, List[Dict]],
    *,
    level: float = 0.0,
    lower: float = 0.0,
) -> Iterator[Example]:
    if random.random() >= level:
        yield example
    else:
        raw_text = example.text
        orig_dict = example.to_dict()
        orig_dict["doc_annotation"]["entities"] = _doc_to_biluo_tags_with_partial(
            example.reference
        )
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
    raw = construct_modified_raw_text(token_dict)
    return raw, token_dict


def make_whitespace_variant(
    nlp: "Language",
    example: Example,
    whitespace: str,
    position: int,
) -> Example:
    """Insert the whitespace token at the specified token offset in the doc.
    This is primarily intended for v2-compatible training data that doesn't
    include links or spans. If the document includes links, spans, or partial
    dependency annotation, it is returned without modifications.

    The augmentation follows the basics of the v2 space attachment policy, but
    without a distinction between "real" and other tokens, so space tokens
    may be attached to space tokens:
    - at the beginning of a sentence attach the space token to the following
      token
    - otherwise attach the space token to the preceding token

    The augmenter does not attempt to consolidate adjacent whitespace in the
    same way that the tokenizer would.

    The following annotation is used for the space token:
    TAG: "_SP"
    MORPH: ""
    POS: "SPACE"
    LEMMA: ORTH
    DEP: "dep"
    SENT_START: False

    The annotation for each attribute is only set for the space token if there
    is already at least partial annotation for that attribute in the original
    example.

    RETURNS (Example): Example with one additional space token.
    """
    example_dict = example.to_dict()
    example_dict["doc_annotation"]["entities"] = _doc_to_biluo_tags_with_partial(
        example.reference
    )
    doc_dict = example_dict.get("doc_annotation", {})
    token_dict = example_dict.get("token_annotation", {})
    # returned unmodified if:
    # - doc is empty
    # - words are not defined
    # - links are defined (only character-based offsets, which is more a quirk
    #   of Example.to_dict than a technical constraint)
    # - spans are defined
    # - there are partial dependencies
    if (
        len(example.reference) == 0
        or "ORTH" not in token_dict
        or len(doc_dict.get("links", [])) > 0
        or len(example.reference.spans) > 0
        or (
            example.reference.has_annotation("DEP")
            and not example.reference.has_annotation("DEP", require_complete=True)
        )
    ):
        return example
    words = token_dict.get("ORTH", [])
    length = len(words)
    assert 0 <= position <= length
    if example.reference.has_annotation("ENT_TYPE"):
        # I-ENTITY if between B/I-ENTITY and I/L-ENTITY otherwise O
        entity = "O"
        if position > 1 and position < length:
            ent_prev = doc_dict["entities"][position - 1]
            ent_next = doc_dict["entities"][position]
            if "-" in ent_prev and "-" in ent_next:
                ent_iob_prev, ent_type_prev = split_bilu_label(ent_prev)
                ent_iob_next, ent_type_next = split_bilu_label(ent_next)
                if (
                    ent_iob_prev in ("B", "I")
                    and ent_iob_next in ("I", "L")
                    and ent_type_prev == ent_type_next
                ):
                    entity = f"I-{ent_type_prev}"
        doc_dict["entities"].insert(position, entity)
    else:
        del doc_dict["entities"]
    token_dict["ORTH"].insert(position, whitespace)
    token_dict["SPACY"].insert(position, False)
    if example.reference.has_annotation("TAG"):
        token_dict["TAG"].insert(position, "_SP")
    else:
        del token_dict["TAG"]
    if example.reference.has_annotation("LEMMA"):
        token_dict["LEMMA"].insert(position, whitespace)
    else:
        del token_dict["LEMMA"]
    if example.reference.has_annotation("POS"):
        token_dict["POS"].insert(position, "SPACE")
    else:
        del token_dict["POS"]
    if example.reference.has_annotation("MORPH"):
        token_dict["MORPH"].insert(position, "")
    else:
        del token_dict["MORPH"]
    if example.reference.has_annotation("DEP", require_complete=True):
        if position == 0:
            token_dict["HEAD"].insert(position, 0)
        else:
            token_dict["HEAD"].insert(position, position - 1)
        for i in range(len(token_dict["HEAD"])):
            if token_dict["HEAD"][i] >= position:
                token_dict["HEAD"][i] += 1
        token_dict["DEP"].insert(position, "dep")
    else:
        del token_dict["HEAD"]
        del token_dict["DEP"]
    if example.reference.has_annotation("SENT_START"):
        token_dict["SENT_START"].insert(position, False)
    else:
        del token_dict["SENT_START"]
    raw = construct_modified_raw_text(token_dict)
    return Example.from_dict(nlp.make_doc(raw), example_dict)


def construct_modified_raw_text(token_dict):
    """Construct modified raw text from words and spaces."""
    raw = ""
    for orth, spacy in zip(token_dict["ORTH"], token_dict["SPACY"]):
        raw += orth
        if spacy:
            raw += " "
    return raw

from typing import Callable, Iterator, Dict, List, Tuple, Optional, TYPE_CHECKING
import random
import itertools
import copy
from functools import partial

from ..util import registry, logger
from ..tokens import Doc
from .example import Example
from ..lookups import Lookups
from ..errors import Errors

if TYPE_CHECKING:
    from ..language import Language  # noqa: F401


@registry.augmenters("spacy.orth_variants.v1")
def create_orth_variants_augmenter(
    level: float, lower: float, lookups: Optional[Lookups] = None,
) -> Callable[["Language", Example], Iterator[Example]]:
    """Create a data augmentation callback that uses orth-variant replacement.
    The callback can be added to a corpus or other data iterator during training.
    """
    return partial(orth_variants_augmenter, level=level, lower=lower, lookups=lookups)


def dont_augment(nlp: "Language", example: Example) -> Iterator[Example]:
    yield example


def orth_variants_augmenter(
    nlp: "Language",
    example: Example,
    *,
    level: float = 0.0,
    lower: float = 0.0,
    lookups: Optional[Lookups] = None,
) -> Iterator[Example]:
    table_name = "orth_variants"
    if lookups is not None:
        orth_variants = lookups.get_table(table_name, {})
        logger.debug("Using data augmentation orth variants from provided lookups")
    else:
        orth_variants = nlp.vocab.lookups.get_table(table_name, {})
        logger.debug("Using data augmentation orth variants from default vocab lookups")
        if not orth_variants:
            raise ValueError(Errors.E912.format(lang=nlp.lang))
    if random.random() >= level:
        yield example
    else:
        raw_text = example.text
        orig_dict = example.to_dict()
        if not orig_dict["token_annotation"]:
            yield example
        else:
            variant_text, variant_token_annot = make_orth_variants(
                nlp,
                raw_text,
                orig_dict["token_annotation"],
                orth_variants,
                lower=raw_text is not None and random.random() < lower,
            )
            if variant_text:
                doc = nlp.make_doc(variant_text)
            else:
                doc = Doc(nlp.vocab, words=variant_token_annot["ORTH"])
                variant_token_annot["ORTH"] = [w.text for w in doc]
                variant_token_annot["SPACY"] = [w.whitespace_ for w in doc]
            orig_dict["token_annotation"] = variant_token_annot
            yield example.from_dict(doc, orig_dict)


def make_orth_variants(
    nlp: "Language",
    raw: str,
    token_dict: Dict[str, List[str]],
    orth_variants: Dict[str, list],
    *,
    lower: bool = False,
) -> Tuple[str, Dict[str, List[str]]]:
    orig_token_dict = copy.deepcopy(token_dict)
    ndsv = orth_variants.get("single", [])
    ndpv = orth_variants.get("paired", [])
    words = token_dict.get("words", [])
    tags = token_dict.get("tags", [])
    # keep unmodified if words or tags are not defined
    if words and tags:
        if lower:
            words = [w.lower() for w in words]
        # single variants
        punct_choices = [random.choice(x["variants"]) for x in ndsv]
        for word_idx in range(len(words)):
            for punct_idx in range(len(ndsv)):
                if (
                    tags[word_idx] in ndsv[punct_idx]["tags"]
                    and words[word_idx] in ndsv[punct_idx]["variants"]
                ):
                    words[word_idx] = punct_choices[punct_idx]
        # paired variants
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
        token_dict["words"] = words
        token_dict["tags"] = tags
    # modify raw
    if raw is not None:
        variants = []
        for single_variants in ndsv:
            variants.extend(single_variants["variants"])
        for paired_variants in ndpv:
            variants.extend(
                list(itertools.chain.from_iterable(paired_variants["variants"]))
            )
        # store variants in reverse length order to be able to prioritize
        # longer matches (e.g., "---" before "--")
        variants = sorted(variants, key=lambda x: len(x))
        variants.reverse()
        variant_raw = ""
        raw_idx = 0
        # add initial whitespace
        while raw_idx < len(raw) and raw[raw_idx].isspace():
            variant_raw += raw[raw_idx]
            raw_idx += 1
        for word in words:
            match_found = False
            # skip whitespace words
            if word.isspace():
                match_found = True
            # add identical word
            elif word not in variants and raw[raw_idx:].startswith(word):
                variant_raw += word
                raw_idx += len(word)
                match_found = True
            # add variant word
            else:
                for variant in variants:
                    if not match_found and raw[raw_idx:].startswith(variant):
                        raw_idx += len(variant)
                        variant_raw += word
                        match_found = True
            # something went wrong, abort
            # (add a warning message?)
            if not match_found:
                return raw, orig_token_dict
            # add following whitespace
            while raw_idx < len(raw) and raw[raw_idx].isspace():
                variant_raw += raw[raw_idx]
                raw_idx += 1
        raw = variant_raw
    return raw, token_dict

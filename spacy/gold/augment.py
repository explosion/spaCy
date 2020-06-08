import random
import itertools
from .example import Example
from .annotation import TokenAnnotation


def make_orth_variants(nlp, example, orth_variant_level=0.0):
    if random.random() >= orth_variant_level:
        return example
    if not example.token_annotation:
        return example
    raw = example.text
    lower = False
    if random.random() >= 0.5:
        lower = True
        if raw is not None:
            raw = raw.lower()
    ndsv = nlp.Defaults.single_orth_variants
    ndpv = nlp.Defaults.paired_orth_variants
    # modify words in paragraph_tuples
    variant_example = Example(doc=nlp.make_doc(raw))
    token_annotation = example.token_annotation
    words = token_annotation.words
    tags = token_annotation.tags
    if not words or not tags:
        # add the unmodified annotation
        token_dict = token_annotation.to_dict()
        variant_example.token_annotation = TokenAnnotation(**token_dict)
    else:
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

        token_dict = token_annotation.to_dict()
        token_dict["words"] = words
        token_dict["tags"] = tags
        variant_example.token_annotation = TokenAnnotation(**token_dict)
    # modify raw to match variant_paragraph_tuples
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
        for word in variant_example.token_annotation.words:
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
                return example
            # add following whitespace
            while raw_idx < len(raw) and raw[raw_idx].isspace():
                variant_raw += raw[raw_idx]
                raw_idx += 1
        variant_example.doc = variant_raw
        return variant_example
    return variant_example


def add_noise(orig, noise_level):
    if random.random() >= noise_level:
        return orig
    elif type(orig) == list:
        corrupted = [_corrupt(word, noise_level) for word in orig]
        corrupted = [w for w in corrupted if w]
        return corrupted
    else:
        return "".join(_corrupt(c, noise_level) for c in orig)


def _corrupt(c, noise_level):
    if random.random() >= noise_level:
        return c
    elif c in [".", "'", "!", "?", ","]:
        return "\n"
    else:
        return c.lower()

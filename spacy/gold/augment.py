import random
import itertools


def make_orth_variants_example(nlp, example, orth_variant_level=0.0):  # TODO: naming
    raw_text = example.text
    orig_dict = example.to_dict()
    variant_text, variant_token_annot = make_orth_variants(
        nlp, raw_text, orig_dict["token_annotation"], orth_variant_level
    )
    doc = nlp.make_doc(variant_text)
    orig_dict["token_annotation"] = variant_token_annot
    return example.from_dict(doc, orig_dict)


def make_orth_variants(nlp, raw_text, orig_token_dict, orth_variant_level=0.0):
    if random.random() >= orth_variant_level:
        return raw_text, orig_token_dict
    if not orig_token_dict:
        return raw_text, orig_token_dict
    raw = raw_text
    token_dict = orig_token_dict
    lower = False
    if random.random() >= 0.5:
        lower = True
        if raw is not None:
            raw = raw.lower()
    ndsv = nlp.Defaults.single_orth_variants
    ndpv = nlp.Defaults.paired_orth_variants
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
                return raw_text, orig_token_dict
            # add following whitespace
            while raw_idx < len(raw) and raw[raw_idx].isspace():
                variant_raw += raw[raw_idx]
                raw_idx += 1
        raw = variant_raw
    return raw, token_dict

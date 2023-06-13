import re

from wasabi import Printer

from ...tokens import Doc, Span, Token
from ...training import biluo_tags_to_spans, iob_to_biluo
from ...vocab import Vocab
from .conll_ner_to_docs import n_sents_info


def conllu_to_docs(
    input_data,
    n_sents=10,
    append_morphology=False,
    ner_map=None,
    merge_subtokens=False,
    no_print=False,
    **_
):
    """
    Convert conllu files into JSON format for use with train cli.
    append_morphology parameter enables appending morphology to tags, which is
    useful for languages such as Spanish, where UD tags are not so rich.

    Extract NER tags if available and convert them so that they follow
    BILUO and the Wikipedia scheme
    """
    MISC_NER_PATTERN = "^((?:name|NE)=)?([BILU])-([A-Z_]+)|O$"
    msg = Printer(no_print=no_print)
    n_sents_info(msg, n_sents)
    sent_docs = read_conllx(
        input_data,
        append_morphology=append_morphology,
        ner_tag_pattern=MISC_NER_PATTERN,
        ner_map=ner_map,
        merge_subtokens=merge_subtokens,
    )
    sent_docs_to_merge = []
    for sent_doc in sent_docs:
        sent_docs_to_merge.append(sent_doc)
        if len(sent_docs_to_merge) % n_sents == 0:
            yield Doc.from_docs(sent_docs_to_merge)
            sent_docs_to_merge = []
    if sent_docs_to_merge:
        yield Doc.from_docs(sent_docs_to_merge)


def has_ner(input_data, ner_tag_pattern):
    """
    Check the MISC column for NER tags.
    """
    for sent in input_data.strip().split("\n\n"):
        lines = sent.strip().split("\n")
        if lines:
            while lines[0].startswith("#"):
                lines.pop(0)
            for line in lines:
                parts = line.split("\t")
                id_, word, lemma, pos, tag, morph, head, dep, _1, misc = parts
                for misc_part in misc.split("|"):
                    if re.match(ner_tag_pattern, misc_part):
                        return True
    return False


def read_conllx(
    input_data,
    append_morphology=False,
    merge_subtokens=False,
    ner_tag_pattern="",
    ner_map=None,
):
    """Yield docs, one for each sentence"""
    vocab = Vocab()  # need vocab to make a minimal Doc
    set_ents = has_ner(input_data, ner_tag_pattern)
    for sent in input_data.strip().split("\n\n"):
        lines = sent.strip().split("\n")
        if lines:
            while lines[0].startswith("#"):
                lines.pop(0)
            doc = conllu_sentence_to_doc(
                vocab,
                lines,
                ner_tag_pattern,
                merge_subtokens=merge_subtokens,
                append_morphology=append_morphology,
                ner_map=ner_map,
                set_ents=set_ents,
            )
            yield doc


def get_entities(lines, tag_pattern, ner_map=None):
    """Find entities in the MISC column according to the pattern and map to
    final entity type with `ner_map` if mapping present. Entity tag is 'O' if
    the pattern is not matched.

    lines (str): CONLL-U lines for one sentences
    tag_pattern (str): Regex pattern for entity tag
    ner_map (dict): Map old NER tag names to new ones, '' maps to O.
    RETURNS (list): List of BILUO entity tags
    """
    miscs = []
    for line in lines:
        parts = line.split("\t")
        id_, word, lemma, pos, tag, morph, head, dep, _1, misc = parts
        if "-" in id_ or "." in id_:
            continue
        miscs.append(misc)

    iob = []
    for misc in miscs:
        iob_tag = "O"
        for misc_part in misc.split("|"):
            tag_match = re.match(tag_pattern, misc_part)
            if tag_match:
                prefix = tag_match.group(2)
                suffix = tag_match.group(3)
                if prefix and suffix:
                    iob_tag = prefix + "-" + suffix
                    if ner_map:
                        suffix = ner_map.get(suffix, suffix)
                        if suffix == "":
                            iob_tag = "O"
                        else:
                            iob_tag = prefix + "-" + suffix
                break
        iob.append(iob_tag)
    return iob_to_biluo(iob)


def conllu_sentence_to_doc(
    vocab,
    lines,
    ner_tag_pattern,
    merge_subtokens=False,
    append_morphology=False,
    ner_map=None,
    set_ents=False,
):
    """Create an Example from the lines for one CoNLL-U sentence, merging
    subtokens and appending morphology to tags if required.

    lines (str): The non-comment lines for a CoNLL-U sentence
    ner_tag_pattern (str): The regex pattern for matching NER in MISC col
    RETURNS (Example): An example containing the annotation
    """
    # create a Doc with each subtoken as its own token
    # if merging subtokens, each subtoken orth is the merged subtoken form
    if not Token.has_extension("merged_orth"):
        Token.set_extension("merged_orth", default="")
    if not Token.has_extension("merged_lemma"):
        Token.set_extension("merged_lemma", default="")
    if not Token.has_extension("merged_morph"):
        Token.set_extension("merged_morph", default="")
    if not Token.has_extension("merged_spaceafter"):
        Token.set_extension("merged_spaceafter", default="")
    words, spaces, tags, poses, morphs, lemmas = [], [], [], [], [], []
    heads, deps = [], []
    subtok_word = ""
    in_subtok = False
    for i in range(len(lines)):
        line = lines[i]
        parts = line.split("\t")
        id_, word, lemma, pos, tag, morph, head, dep, _1, misc = parts
        if "." in id_:
            continue
        if "-" in id_:
            in_subtok = True
        if "-" in id_:
            in_subtok = True
            subtok_word = word
            subtok_start, subtok_end = id_.split("-")
            subtok_spaceafter = "SpaceAfter=No" not in misc
            continue
        if merge_subtokens and in_subtok:
            words.append(subtok_word)
        else:
            words.append(word)
        if in_subtok:
            if id_ == subtok_end:
                spaces.append(subtok_spaceafter)
            else:
                spaces.append(False)
        elif "SpaceAfter=No" in misc:
            spaces.append(False)
        else:
            spaces.append(True)
        if in_subtok and id_ == subtok_end:
            subtok_word = ""
            in_subtok = False
        id_ = int(id_) - 1
        head = (int(head) - 1) if head not in ("0", "_") else id_
        tag = pos if tag == "_" else tag
        pos = pos if pos != "_" else ""
        morph = morph if morph != "_" else ""
        dep = "ROOT" if dep == "root" else dep
        lemmas.append(lemma)
        poses.append(pos)
        tags.append(tag)
        morphs.append(morph)
        heads.append(head)
        deps.append(dep)

    doc = Doc(
        vocab,
        words=words,
        spaces=spaces,
        tags=tags,
        pos=poses,
        deps=deps,
        lemmas=lemmas,
        morphs=morphs,
        heads=heads,
    )
    for i in range(len(doc)):
        doc[i]._.merged_orth = words[i]
        doc[i]._.merged_morph = morphs[i]
        doc[i]._.merged_lemma = lemmas[i]
        doc[i]._.merged_spaceafter = spaces[i]
    ents = None
    if set_ents:
        ents = get_entities(lines, ner_tag_pattern, ner_map)
        doc.ents = biluo_tags_to_spans(doc, ents)

    if merge_subtokens:
        doc = merge_conllu_subtokens(lines, doc)

    # create final Doc from custom Doc annotation
    words, spaces, tags, morphs, lemmas, poses = [], [], [], [], [], []
    heads, deps = [], []
    for i, t in enumerate(doc):
        words.append(t._.merged_orth)
        lemmas.append(t._.merged_lemma)
        spaces.append(t._.merged_spaceafter)
        morphs.append(t._.merged_morph)
        if append_morphology and t._.merged_morph:
            tags.append(t.tag_ + "__" + t._.merged_morph)
        else:
            tags.append(t.tag_)
        poses.append(t.pos_)
        heads.append(t.head.i)
        deps.append(t.dep_)

    doc_x = Doc(
        vocab,
        words=words,
        spaces=spaces,
        tags=tags,
        morphs=morphs,
        lemmas=lemmas,
        pos=poses,
        deps=deps,
        heads=heads,
    )
    if set_ents:
        doc_x.ents = [
            Span(doc_x, ent.start, ent.end, label=ent.label) for ent in doc.ents
        ]

    return doc_x


def merge_conllu_subtokens(lines, doc):
    # identify and process all subtoken spans to prepare attrs for merging
    subtok_spans = []
    for line in lines:
        parts = line.split("\t")
        id_, word, lemma, pos, tag, morph, head, dep, _1, misc = parts
        if "-" in id_:
            subtok_start, subtok_end = id_.split("-")
            subtok_span = doc[int(subtok_start) - 1 : int(subtok_end)]
            subtok_spans.append(subtok_span)
            # create merged tag, morph, and lemma values
            tags = []
            morphs = {}
            lemmas = []
            for token in subtok_span:
                tags.append(token.tag_)
                lemmas.append(token.lemma_)
                if token._.merged_morph:
                    for feature in token._.merged_morph.split("|"):
                        field, values = feature.split("=", 1)
                        if field not in morphs:
                            morphs[field] = set()
                        for value in values.split(","):
                            morphs[field].add(value)
            # create merged features for each morph field
            for field, values in morphs.items():
                morphs[field] = field + "=" + ",".join(sorted(values))
            # set the same attrs on all subtok tokens so that whatever head the
            # retokenizer chooses, the final attrs are available on that token
            for token in subtok_span:
                token._.merged_orth = token.orth_
                token._.merged_lemma = " ".join(lemmas)
                token.tag_ = "_".join(tags)
                token._.merged_morph = "|".join(sorted(morphs.values()))
                token._.merged_spaceafter = (
                    True if subtok_span[-1].whitespace_ else False
                )

    with doc.retokenize() as retokenizer:
        for span in subtok_spans:
            retokenizer.merge(span)

    return doc

# coding: utf8
from __future__ import unicode_literals

import re

from spacy.gold import Example
from ...gold import iob_to_biluo


def conllu2json(input_data, n_sents=10, use_morphology=False, lang=None, **_):
    """
    Convert conllu files into JSON format for use with train cli.
    use_morphology parameter enables appending morphology to tags, which is
    useful for languages such as Spanish, where UD tags are not so rich.

    Extract NER tags if available and convert them so that they follow
    BILUO and the Wikipedia scheme
    """
    # by @dvsrepo, via #11 explosion/spacy-dev-resources
    # by @katarkor
    # name=NER is to handle NorNE
    MISC_NER_PATTERN = "\|?(?:name=)?(([A-Z_]+)-([A-Z_]+)|O)\|?"
    docs = []
    raw = ""
    sentences = []
    conll_data = read_conllx(input_data, use_morphology=use_morphology)
    checked_for_ner = False
    has_ner_tags = False
    for i, example in enumerate(conll_data):
        if not checked_for_ner:
            has_ner_tags = is_ner(example.token_annotation.entities[0],
                    MISC_NER_PATTERN)
            checked_for_ner = True
        raw += example.text
        sentences.append(generate_sentence(example.token_annotation,
                has_ner_tags, MISC_NER_PATTERN))
        # Real-sized documents could be extracted using the comments on the
        # conllu document
        if len(sentences) % n_sents == 0:
            doc = create_doc(raw, sentences, i)
            docs.append(doc)
            raw = ""
            sentences = []
    return docs


def is_ner(tag, tag_pattern):
    """
    Check the 10th column of the first token to determine if the file contains
    NER tags
    """
    tag_match = re.search(tag_pattern, tag)
    if tag_match:
        return True
    elif tag == "O":
        return True
    else:
        return False


def read_conllx(input_data, use_morphology=False, n=0):
    """ Yield example data points, one for each sentence """
    i = 0
    for sent in input_data.strip().split("\n\n"):
        lines = sent.strip().split("\n")
        if lines:
            while lines[0].startswith("#"):
                lines.pop(0)
            ids, words, tags, heads, deps, ents = [], [], [], [], [], []
            spaces = []
            for line in lines:
                parts = line.split("\t")
                id_, word, lemma, pos, tag, morph, head, dep, _1, misc = parts
                if "-" in id_ or "." in id_:
                    continue
                try:
                    id_ = int(id_) - 1
                    head = (int(head) - 1) if head != "0" else id_
                    dep = "ROOT" if dep == "root" else dep
                    tag = pos if tag == "_" else tag
                    tag = tag + "__" + morph if use_morphology else tag
                    ent = misc if misc else "O"

                    ids.append(id_)
                    words.append(word)
                    tags.append(tag)
                    heads.append(head)
                    deps.append(dep)
                    ents.append(ent)
                    if "SpaceAfter=No" in misc:
                        spaces.append(False)
                    else:
                        spaces.append(True)
                except:  # noqa: E722
                    print(line)
                    raise
            raw = ""
            for word, space in zip(words, spaces):
                raw += word
                if space:
                    raw += " "
            example = Example(doc=raw)
            example.set_token_annotation(ids=ids, words=words, tags=tags,
                                         heads=heads, deps=deps, entities=ents)
            yield example
            i += 1
            if 1 <= n <= i:
                break


def simplify_tags(iob, tag_pattern):
    """
    Simplify tags obtained from the dataset in order to follow Wikipedia
    scheme (PER, LOC, ORG, MISC). 'PER', 'LOC' and 'ORG' keep their tags, while
    'GPE_LOC' is simplified to 'LOC', 'GPE_ORG' to 'ORG' and all remaining tags to
    'MISC'.
    """
    new_iob = []
    for tag in iob:
        tag_match = re.search(tag_pattern, tag)
        new_tag = "O"
        if tag_match:
            prefix = tag_match.group(2)
            suffix = tag_match.group(3)
            if prefix and suffix:
                if suffix == "GPE_LOC":
                    suffix = "LOC"
                elif suffix == "GPE_ORG":
                    suffix = "ORG"
                elif suffix != "PER" and suffix != "LOC" and suffix != "ORG":
                    suffix = "MISC"
                new_tag = prefix + "-" + suffix
        new_iob.append(new_tag)
    return new_iob


def generate_sentence(token_annotation, has_ner_tags, tag_pattern):
    sentence = {}
    tokens = []
    if has_ner_tags:
        iob = simplify_tags(token_annotation.entities, tag_pattern)
        biluo = iob_to_biluo(iob)
    for i, id in enumerate(token_annotation.ids):
        token = {}
        token["id"] = id
        token["orth"] = token_annotation.words[i]
        token["tag"] = token_annotation.tags[i]
        token["head"] = token_annotation.heads[i] - id
        token["dep"] = token_annotation.deps[i]
        if has_ner_tags:
            token["ner"] = biluo[i]
        tokens.append(token)
    sentence["tokens"] = tokens
    return sentence


def create_doc(raw, sentences, id):
    doc = {}
    paragraph = {}
    doc["id"] = id
    doc["paragraphs"] = []
    paragraph["raw"] = raw.strip()
    paragraph["sentences"] = sentences
    doc["paragraphs"].append(paragraph)
    return doc

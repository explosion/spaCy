# coding: utf8
from __future__ import unicode_literals

import re

from ...gold import iob_to_biluo


def conllu2json(input_data, n_sents=10, use_morphology=False, lang=None):
    """
    Convert conllu files into JSON format for use with train cli.
    use_morphology parameter enables appending morphology to tags, which is
    useful for languages such as Spanish, where UD tags are not so rich.

    Extract NER tags if available and convert them so that they follow
    BILUO and the Wikipedia scheme
    """
    # by @dvsrepo, via #11 explosion/spacy-dev-resources
    # by @katarkor
    docs = []
    sentences = []
    conll_tuples = read_conllx(input_data, use_morphology=use_morphology)
    checked_for_ner = False
    has_ner_tags = False
    for i, (raw_text, tokens) in enumerate(conll_tuples):
        sentence, brackets = tokens[0]
        if not checked_for_ner:
            has_ner_tags = is_ner(sentence[5][0])
            checked_for_ner = True
        sentences.append(generate_sentence(sentence, has_ner_tags))
        # Real-sized documents could be extracted using the comments on the
        # conluu document
        if len(sentences) % n_sents == 0:
            doc = create_doc(sentences, i)
            docs.append(doc)
            sentences = []
    return docs


def is_ner(tag):
    """
    Check the 10th column of the first token to determine if the file contains
    NER tags
    """
    tag_match = re.match("([A-Z_]+)-([A-Z_]+)", tag)
    if tag_match:
        return True
    elif tag == "O":
        return True
    else:
        return False


def read_conllx(input_data, use_morphology=False, n=0):
    i = 0
    for sent in input_data.strip().split("\n\n"):
        lines = sent.strip().split("\n")
        if lines:
            while lines[0].startswith("#"):
                lines.pop(0)
            tokens = []
            for line in lines:

                parts = line.split("\t")
                id_, word, lemma, pos, tag, morph, head, dep, _1, iob = parts
                if "-" in id_ or "." in id_:
                    continue
                try:
                    id_ = int(id_) - 1
                    head = (int(head) - 1) if head != "0" else id_
                    dep = "ROOT" if dep == "root" else dep
                    tag = pos if tag == "_" else tag
                    tag = tag + "__" + morph if use_morphology else tag
                    iob = iob if iob else "O"
                    tokens.append((id_, word, tag, head, dep, iob))
                except:  # noqa: E722
                    print(line)
                    raise
            tuples = [list(t) for t in zip(*tokens)]
            yield (None, [[tuples, []]])
            i += 1
            if n >= 1 and i >= n:
                break


def simplify_tags(iob):
    """
    Simplify tags obtained from the dataset in order to follow Wikipedia
    scheme (PER, LOC, ORG, MISC). 'PER', 'LOC' and 'ORG' keep their tags, while
    'GPE_LOC' is simplified to 'LOC', 'GPE_ORG' to 'ORG' and all remaining tags to
    'MISC'.
    """
    new_iob = []
    for tag in iob:
        tag_match = re.match("([A-Z_]+)-([A-Z_]+)", tag)
        if tag_match:
            prefix = tag_match.group(1)
            suffix = tag_match.group(2)
            if suffix == "GPE_LOC":
                suffix = "LOC"
            elif suffix == "GPE_ORG":
                suffix = "ORG"
            elif suffix != "PER" and suffix != "LOC" and suffix != "ORG":
                suffix = "MISC"
            tag = prefix + "-" + suffix
        new_iob.append(tag)
    return new_iob


def generate_sentence(sent, has_ner_tags):
    (id_, word, tag, head, dep, iob) = sent
    sentence = {}
    tokens = []
    if has_ner_tags:
        iob = simplify_tags(iob)
        biluo = iob_to_biluo(iob)
    for i, id in enumerate(id_):
        token = {}
        token["id"] = id
        token["orth"] = word[i]
        token["tag"] = tag[i]
        token["head"] = head[i] - id
        token["dep"] = dep[i]
        if has_ner_tags:
            token["ner"] = biluo[i]
        tokens.append(token)
    sentence["tokens"] = tokens
    return sentence


def create_doc(sentences, id):
    doc = {}
    paragraph = {}
    doc["id"] = id
    doc["paragraphs"] = []
    paragraph["sentences"] = sentences
    doc["paragraphs"].append(paragraph)
    return doc

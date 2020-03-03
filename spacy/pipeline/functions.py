# coding: utf8
from __future__ import unicode_literals

from ..language import component
from ..matcher import Matcher
from ..util import filter_spans


@component(
    "merge_noun_chunks",
    requires=["token.dep", "token.tag", "token.pos"],
    retokenizes=True,
)
def merge_noun_chunks(doc):
    """Merge noun chunks into a single token.

    doc (Doc): The Doc object.
    RETURNS (Doc): The Doc object with merged noun chunks.

    DOCS: https://spacy.io/api/pipeline-functions#merge_noun_chunks
    """
    if not doc.is_parsed:
        return doc
    with doc.retokenize() as retokenizer:
        for np in doc.noun_chunks:
            attrs = {"tag": np.root.tag, "dep": np.root.dep}
            retokenizer.merge(np, attrs=attrs)
    return doc


@component(
    "merge_entities",
    requires=["doc.ents", "token.ent_iob", "token.ent_type"],
    retokenizes=True,
)
def merge_entities(doc):
    """Merge entities into a single token.

    doc (Doc): The Doc object.
    RETURNS (Doc): The Doc object with merged entities.

    DOCS: https://spacy.io/api/pipeline-functions#merge_entities
    """
    with doc.retokenize() as retokenizer:
        for ent in doc.ents:
            attrs = {"tag": ent.root.tag, "dep": ent.root.dep, "ent_type": ent.label}
            retokenizer.merge(ent, attrs=attrs)
    return doc


@component("merge_subtokens", requires=["token.dep"], retokenizes=True)
def merge_subtokens(doc, label="subtok"):
    """Merge subtokens into a single token.

    doc (Doc): The Doc object.
    label (unicode): The subtoken dependency label.
    RETURNS (Doc): The Doc object with merged subtokens.

    DOCS: https://spacy.io/api/pipeline-functions#merge_subtokens
    """
    merger = Matcher(doc.vocab)
    merger.add("SUBTOK", None, [{"DEP": label, "op": "+"}])
    matches = merger(doc)
    spans = filter_spans([doc[start : end + 1] for _, start, end in matches])
    with doc.retokenize() as retokenizer:
        for span in spans:
            retokenizer.merge(span)
    return doc

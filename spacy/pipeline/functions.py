from ..language import Language
from ..matcher import Matcher
from ..tokens import Doc
from ..util import filter_spans


@Language.component(
    "merge_noun_chunks",
    requires=["token.dep", "token.tag", "token.pos"],
    retokenizes=True,
)
def merge_noun_chunks(doc: Doc) -> Doc:
    """Merge noun chunks into a single token.

    doc (Doc): The Doc object.
    RETURNS (Doc): The Doc object with merged noun chunks.

    DOCS: https://nightly.spacy.io/api/pipeline-functions#merge_noun_chunks
    """
    if not doc.has_annotation("DEP"):
        return doc
    with doc.retokenize() as retokenizer:
        for np in doc.noun_chunks:
            attrs = {"tag": np.root.tag, "dep": np.root.dep}
            retokenizer.merge(np, attrs=attrs)
    return doc


@Language.component(
    "merge_entities",
    requires=["doc.ents", "token.ent_iob", "token.ent_type"],
    retokenizes=True,
)
def merge_entities(doc: Doc):
    """Merge entities into a single token.

    doc (Doc): The Doc object.
    RETURNS (Doc): The Doc object with merged entities.

    DOCS: https://nightly.spacy.io/api/pipeline-functions#merge_entities
    """
    with doc.retokenize() as retokenizer:
        for ent in doc.ents:
            attrs = {"tag": ent.root.tag, "dep": ent.root.dep, "ent_type": ent.label}
            retokenizer.merge(ent, attrs=attrs)
    return doc


@Language.component("merge_subtokens", requires=["token.dep"], retokenizes=True)
def merge_subtokens(doc: Doc, label: str = "subtok") -> Doc:
    """Merge subtokens into a single token.

    doc (Doc): The Doc object.
    label (str): The subtoken dependency label.
    RETURNS (Doc): The Doc object with merged subtokens.

    DOCS: https://nightly.spacy.io/api/pipeline-functions#merge_subtokens
    """
    # TODO: make stateful component with "label" config
    merger = Matcher(doc.vocab)
    merger.add("SUBTOK", [[{"DEP": label, "op": "+"}]])
    matches = merger(doc)
    spans = filter_spans([doc[start : end + 1] for _, start, end in matches])
    with doc.retokenize() as retokenizer:
        for span in spans:
            retokenizer.merge(span)
    return doc

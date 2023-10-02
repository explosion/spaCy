# cython: profile=False
import warnings

import srsly

from .. import util
from ..errors import Warnings
from ..tokens import Doc
from .iob_utils import offsets_to_biluo_tags


def docs_to_json(docs, doc_id=0, ner_missing_tag="O"):
    """Convert a list of Doc objects into the JSON-serializable format used by
    the spacy train command.

    docs (iterable / Doc): The Doc object(s) to convert.
    doc_id (int): Id for the JSON.
    RETURNS (dict): The data in spaCy's JSON format
        - each input doc will be treated as a paragraph in the output doc
    """
    if isinstance(docs, Doc):
        docs = [docs]
    json_doc = {"id": doc_id, "paragraphs": []}
    for i, doc in enumerate(docs):
        raw = None if doc.has_unknown_spaces else doc.text
        json_para = {
            'raw': raw,
            "sentences": [],
            "cats": [],
            "entities": [],
            "links": []
        }
        for cat, val in doc.cats.items():
            json_cat = {"label": cat, "value": val}
            json_para["cats"].append(json_cat)
        # warning: entities information is currently duplicated as
        # doc-level "entities" and token-level "ner"
        for ent in doc.ents:
            ent_tuple = (ent.start_char, ent.end_char, ent.label_)
            json_para["entities"].append(ent_tuple)
            if ent.kb_id_:
                link_dict = {(ent.start_char, ent.end_char): {ent.kb_id_: 1.0}}
                json_para["links"].append(link_dict)
        biluo_tags = offsets_to_biluo_tags(
            doc, json_para["entities"], missing=ner_missing_tag
        )
        attrs = ("TAG", "POS", "MORPH", "LEMMA", "DEP", "ENT_IOB")
        include_annotation = {attr: doc.has_annotation(attr) for attr in attrs}
        for j, sent in enumerate(doc.sents):
            json_sent = {"tokens": [], "brackets": []}
            for token in sent:
                json_token = {
                    "id": token.i, "orth": token.text, "space": token.whitespace_
                }
                if include_annotation["TAG"]:
                    json_token["tag"] = token.tag_
                if include_annotation["POS"]:
                    json_token["pos"] = token.pos_
                if include_annotation["MORPH"]:
                    json_token["morph"] = str(token.morph)
                if include_annotation["LEMMA"]:
                    json_token["lemma"] = token.lemma_
                if include_annotation["DEP"]:
                    json_token["head"] = token.head.i-token.i
                    json_token["dep"] = token.dep_
                if include_annotation["ENT_IOB"]:
                    json_token["ner"] = biluo_tags[token.i]
                json_sent["tokens"].append(json_token)
            json_para["sentences"].append(json_sent)
        json_doc["paragraphs"].append(json_para)
    return json_doc


def read_json_file(loc, docs_filter=None, limit=None):
    """Read Example dictionaries from a json file or directory."""
    loc = util.ensure_path(loc)
    if loc.is_dir():
        for filename in sorted(loc.iterdir()):
            yield from read_json_file(loc / filename, limit=limit)
    else:
        with loc.open("rb") as file_:
            utf8_str = file_.read()
        for json_doc in json_iterate(utf8_str):
            if docs_filter is not None and not docs_filter(json_doc):
                continue
            for json_paragraph in json_to_annotations(json_doc):
                yield json_paragraph


def json_to_annotations(doc):
    """Convert an item in the JSON-formatted training data to the format
    used by Example.

    doc (dict): One entry in the training data.
    YIELDS (tuple): The reformatted data - one training example per paragraph
    """
    for paragraph in doc["paragraphs"]:
        example = {"text": paragraph.get("raw", None)}
        words = []
        spaces = []
        ids = []
        tags = []
        ner_tags = []
        pos = []
        morphs = []
        lemmas = []
        heads = []
        labels = []
        sent_starts = []
        brackets = []
        for sent in paragraph["sentences"]:
            sent_start_i = len(words)
            for i, token in enumerate(sent["tokens"]):
                words.append(token["orth"])
                spaces.append(token.get("space", None))
                ids.append(token.get('id', sent_start_i + i))
                tags.append(token.get("tag", None))
                pos.append(token.get("pos", None))
                morphs.append(token.get("morph", None))
                lemmas.append(token.get("lemma", None))
                if "head" in token:
                    heads.append(token["head"] + sent_start_i + i)
                else:
                    heads.append(None)
                if "dep" in token:
                    labels.append(token["dep"])
                    # Ensure ROOT label is case-insensitive
                    if labels[-1].lower() == "root":
                        labels[-1] = "ROOT"
                else:
                    labels.append(None)
                ner_tags.append(token.get("ner", None))
                if i == 0:
                    sent_starts.append(1)
                else:
                    sent_starts.append(-1)
            if "brackets" in sent:
                brackets.extend(
                    (
                        b["first"] + sent_start_i,
                        b["last"] + sent_start_i,
                        b["label"]
                    )
                    for b in sent["brackets"]
                )

        example["token_annotation"] = dict(
            ids=ids,
            words=words,
            spaces=spaces,
            sent_starts=sent_starts,
            brackets=brackets
        )
        # avoid including dummy values that looks like gold info was present
        if any(tags):
            example["token_annotation"]["tags"] = tags
        if any(pos):
            example["token_annotation"]["pos"] = pos
        if any(morphs):
            example["token_annotation"]["morphs"] = morphs
        if any(lemmas):
            example["token_annotation"]["lemmas"] = lemmas
        if any(head is not None for head in heads):
            example["token_annotation"]["heads"] = heads
        if any(labels):
            example["token_annotation"]["deps"] = labels

        cats = {}
        for cat in paragraph.get("cats", {}):
            cats[cat["label"]] = cat["value"]
        example["doc_annotation"] = dict(
            cats=cats,
            entities=ner_tags,
            links=paragraph.get("links", [])
        )
        yield example


def json_iterate(bytes utf8_str):
    # We should've made these files jsonl...But since we didn't, parse out
    # the docs one-by-one to reduce memory usage.
    # It's okay to read in the whole file -- just don't parse it into JSON.
    cdef long file_length = len(utf8_str)
    if file_length > 2 ** 30:
        warnings.warn(Warnings.W027.format(size=file_length))

    raw = <char*>utf8_str
    cdef int square_depth = 0
    cdef int curly_depth = 0
    cdef int inside_string = 0
    cdef int escape = 0
    cdef long start = -1
    cdef char c
    cdef char quote = ord('"')
    cdef char backslash = ord("\\")
    cdef char open_square = ord("[")
    cdef char close_square = ord("]")
    cdef char open_curly = ord("{")
    cdef char close_curly = ord("}")
    for i in range(file_length):
        c = raw[i]
        if escape:
            escape = False
            continue
        if c == backslash:
            escape = True
            continue
        if c == quote:
            inside_string = not inside_string
            continue
        if inside_string:
            continue
        if c == open_square:
            square_depth += 1
        elif c == close_square:
            square_depth -= 1
        elif c == open_curly:
            if square_depth == 1 and curly_depth == 0:
                start = i
            curly_depth += 1
        elif c == close_curly:
            curly_depth -= 1
            if square_depth == 1 and curly_depth == 0:
                substr = utf8_str[start : i + 1].decode("utf8")
                yield srsly.json_loads(substr)
                start = -1

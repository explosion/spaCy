import warnings
import srsly
from .. import util
from ..errors import Warnings
from ..tokens import Token, Doc
from .iob_utils import biluo_tags_from_offsets


def merge_sents(sents):
    m_deps = [[], [], [], [], [], []]
    m_cats = {}
    m_brackets = []
    i = 0
    for (ids, words, tags, heads, labels, ner), (cats, brackets) in sents:
        m_deps[0].extend(id_ + i for id_ in ids)
        m_deps[1].extend(words)
        m_deps[2].extend(tags)
        m_deps[3].extend(head + i for head in heads)
        m_deps[4].extend(labels)
        m_deps[5].extend(ner)
        m_brackets.extend((b["first"] + i, b["last"] + i, b["label"])
                          for b in brackets)
        m_cats.update(cats)
        i += len(ids)
    return [(m_deps, (m_cats, m_brackets))]


def docs_to_json(docs, id=0, ner_missing_tag="O"):
    """Convert a list of Doc objects into the JSON-serializable format used by
    the spacy train command.

    docs (iterable / Doc): The Doc object(s) to convert.
    id (int): Id for the JSON.
    RETURNS (dict): The data in spaCy's JSON format
        - each input doc will be treated as a paragraph in the output doc
    """
    if isinstance(docs, Doc):
        docs = [docs]
    json_doc = {"id": id, "paragraphs": []}
    for i, doc in enumerate(docs):
        json_para = {'raw': doc.text, "sentences": [], "cats": []}
        for cat, val in doc.cats.items():
            json_cat = {"label": cat, "value": val}
            json_para["cats"].append(json_cat)
        ent_offsets = [(e.start_char, e.end_char, e.label_) for e in doc.ents]
        biluo_tags = biluo_tags_from_offsets(doc, ent_offsets, missing=ner_missing_tag)
        for j, sent in enumerate(doc.sents):
            json_sent = {"tokens": [], "brackets": []}
            for token in sent:
                json_token = {"id": token.i, "orth": token.text}
                if doc.is_tagged:
                    json_token["tag"] = token.tag_
                    json_token["pos"] = token.pos_
                    json_token["morph"] = token.morph_
                    json_token["lemma"] = token.lemma_
                if doc.is_parsed:
                    json_token["head"] = token.head.i-token.i
                    json_token["dep"] = token.dep_
                json_token["ner"] = biluo_tags[token.i]
                json_sent["tokens"].append(json_token)
            json_para["sentences"].append(json_sent)
        json_doc["paragraphs"].append(json_para)
    return json_doc


def read_json_file(loc, docs_filter=None, limit=None):
    loc = util.ensure_path(loc)
    if loc.is_dir():
        for filename in loc.iterdir():
            yield from read_json_file(loc / filename, limit=limit)
    else:
        for doc in json_iterate(loc):
            if docs_filter is not None and not docs_filter(doc):
                continue
            for json_data in json_to_examples(doc):
                yield json_data


def json_to_annotations(doc):
    """Convert an item in the JSON-formatted training data to the format
    used by GoldParse.

    doc (dict): One entry in the training data.
    YIELDS (tuple): The reformatted data - one training example per paragraph
    """
    for paragraph in doc["paragraphs"]:
        example = {"text": paragraph.get("raw", None)}
        words = []
        ids = []
        tags = []
        pos = []
        morphs = []
        lemmas = []
        heads = []
        labels = []
        ner = []
        sent_starts = []
        brackets = []
        for sent in paragraph["sentences"]:
            sent_start_i = len(words)
            for i, token in enumerate(sent["tokens"]):
                words.append(token["orth"])
                ids.append(token.get('id', sent_start_i + i))
                tags.append(token.get('tag', "-"))
                pos.append(token.get("pos", ""))
                morphs.append(token.get("morph", ""))
                lemmas.append(token.get("lemma", ""))
                heads.append(token.get("head", 0) + sent_start_i + i)
                labels.append(token.get("dep", ""))
                # Ensure ROOT label is case-insensitive
                if labels[-1].lower() == "root":
                    labels[-1] = "ROOT"
                ner.append(token.get("ner", "-"))
                if i == 0:
                    sent_starts.append(1)
                else:
                    sent_starts.append(0)
            if "brackets" in sent:
                brackets.extend((b["first"] + sent_start_i,
                                 b["last"] + sent_start_i, b["label"])
                                 for b in sent["brackets"])
        cats = {}
        for cat in paragraph.get("cats", {}):
            cats[cat["label"]] = cat["value"]
        example["token_annotation"] = dict(
            ids=ids,
            words=words,
            tags=tags,
            pos=pos,
            morphs=morphs,
            lemmas=lemmas,
            heads=heads,
            deps=labels,
            entities=ner,
            sent_starts=sent_starts,
            brackets=brackets
        )
        example["doc_annotation"] = dict(cats=cats)
        yield example



def json_iterate(loc):
    # We should've made these files jsonl...But since we didn't, parse out
    # the docs one-by-one to reduce memory usage.
    # It's okay to read in the whole file -- just don't parse it into JSON.
    cdef bytes py_raw
    loc = util.ensure_path(loc)
    with loc.open("rb") as file_:
        py_raw = file_.read()
    cdef long file_length = len(py_raw)
    if file_length > 2 ** 30:
        warnings.warn(Warnings.W027.format(size=file_length))

    raw = <char*>py_raw
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
                py_str = py_raw[start : i + 1].decode("utf8")
                try:
                    yield srsly.json_loads(py_str)
                except Exception:
                    print(py_str)
                    raise
                start = -1

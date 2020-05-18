# cython: profile=True
import re
import random
import numpy
import tempfile
import shutil
import itertools
from pathlib import Path
import srsly
import warnings

from .syntax import nonproj
from .tokens import Doc, Span
from .errors import Errors, AlignmentError, Warnings
from . import util


punct_re = re.compile(r"\W")


def tags_to_entities(tags):
    entities = []
    start = None
    for i, tag in enumerate(tags):
        if tag is None:
            continue
        if tag.startswith("O"):
            # TODO: We shouldn't be getting these malformed inputs. Fix this.
            if start is not None:
                start = None
            continue
        elif tag == "-":
            continue
        elif tag.startswith("I"):
            if start is None:
                raise ValueError(Errors.E067.format(tags=tags[:i + 1]))
            continue
        if tag.startswith("U"):
            entities.append((tag[2:], i, i))
        elif tag.startswith("B"):
            start = i
        elif tag.startswith("L"):
            entities.append((tag[2:], start, i))
            start = None
        else:
            raise ValueError(Errors.E068.format(tag=tag))
    return entities


def _normalize_for_alignment(tokens):
    tokens = [w.replace(" ", "").lower() for w in tokens]
    output = []
    for token in tokens:
        token = token.replace(" ", "").lower()
        output.append(token)
    return output


def align(tokens_a, tokens_b):
    """Calculate alignment tables between two tokenizations.

    tokens_a (List[str]): The candidate tokenization.
    tokens_b (List[str]): The reference tokenization.
    RETURNS: (tuple): A 5-tuple consisting of the following information:
      * cost (int): The number of misaligned tokens.
      * a2b (List[int]): Mapping of indices in `tokens_a` to indices in `tokens_b`.
        For instance, if `a2b[4] == 6`, that means that `tokens_a[4]` aligns
        to `tokens_b[6]`. If there's no one-to-one alignment for a token,
        it has the value -1.
      * b2a (List[int]): The same as `a2b`, but mapping the other direction.
      * a2b_multi (Dict[int, int]): A dictionary mapping indices in `tokens_a`
        to indices in `tokens_b`, where multiple tokens of `tokens_a` align to
        the same token of `tokens_b`.
      * b2a_multi (Dict[int, int]): As with `a2b_multi`, but mapping the other
            direction.
    """
    tokens_a = _normalize_for_alignment(tokens_a)
    tokens_b = _normalize_for_alignment(tokens_b)
    cost = 0
    a2b = numpy.empty(len(tokens_a), dtype="i")
    b2a = numpy.empty(len(tokens_b), dtype="i")
    a2b.fill(-1)
    b2a.fill(-1)
    a2b_multi = {}
    b2a_multi = {}
    i = 0
    j = 0
    offset_a = 0
    offset_b = 0
    while i < len(tokens_a) and j < len(tokens_b):
        a = tokens_a[i][offset_a:]
        b = tokens_b[j][offset_b:]
        if a == b:
            if offset_a == offset_b == 0:
                a2b[i] = j
                b2a[j] = i
            elif offset_a == 0:
                cost += 2
                a2b_multi[i] = j
            elif offset_b == 0:
                cost += 2
                b2a_multi[j] = i
            offset_a = offset_b = 0
            i += 1
            j += 1
        elif a == "":
            assert offset_a == 0
            cost += 1
            i += 1
        elif b == "":
            assert offset_b == 0
            cost += 1
            j += 1
        elif b.startswith(a):
            cost += 1
            if offset_a == 0:
                a2b_multi[i] = j
            i += 1
            offset_a = 0
            offset_b += len(a)
        elif a.startswith(b):
            cost += 1
            if offset_b == 0:
                b2a_multi[j] = i
            j += 1
            offset_b = 0
            offset_a += len(b)
        else:
            assert "".join(tokens_a) != "".join(tokens_b)
            raise AlignmentError(Errors.E186.format(tok_a=tokens_a, tok_b=tokens_b))
    return cost, a2b, b2a, a2b_multi, b2a_multi


class GoldCorpus(object):
    """An annotated corpus, using the JSON file format. Manages
    annotations for tagging, dependency parsing and NER.

    DOCS: https://spacy.io/api/goldcorpus
    """
    def __init__(self, train, dev, gold_preproc=False, limit=None):
        """Create a GoldCorpus.

        train (unicode or Path): File or directory of training data.
        dev (unicode or Path): File or directory of development data.
        RETURNS (GoldCorpus): The newly created object.
        """
        self.limit = limit
        if isinstance(train, str) or isinstance(train, Path):
            train = self.read_examples(self.walk_corpus(train))
            dev = self.read_examples(self.walk_corpus(dev))
        # Write temp directory with one doc per file, so we can shuffle and stream
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.write_msgpack(self.tmp_dir / "train", train, limit=self.limit)
        self.write_msgpack(self.tmp_dir / "dev", dev, limit=self.limit)

    def __del__(self):
        shutil.rmtree(self.tmp_dir)

    @staticmethod
    def write_msgpack(directory, examples, limit=0):
        if not directory.exists():
            directory.mkdir()
        n = 0
        for i, example in enumerate(examples):
            ex_dict = example.to_dict()
            text = example.text
            srsly.write_msgpack(directory / f"{i}.msg", (text, ex_dict))
            n += 1
            if limit and n >= limit:
                break

    @staticmethod
    def walk_corpus(path):
        path = util.ensure_path(path)
        if not path.is_dir():
            return [path]
        paths = [path]
        locs = []
        seen = set()
        for path in paths:
            if str(path) in seen:
                continue
            seen.add(str(path))
            if path.parts[-1].startswith("."):
                continue
            elif path.is_dir():
                paths.extend(path.iterdir())
            elif path.parts[-1].endswith((".json", ".jsonl")):
                locs.append(path)
        return locs

    @staticmethod
    def read_examples(locs, limit=0):
        """ Yield training examples """
        i = 0
        for loc in locs:
            loc = util.ensure_path(loc)
            file_name = loc.parts[-1]
            if file_name.endswith("json"):
                examples = read_json_file(loc)
            elif file_name.endswith("jsonl"):
                gold_tuples = srsly.read_jsonl(loc)
                first_gold_tuple = next(gold_tuples)
                gold_tuples = itertools.chain([first_gold_tuple], gold_tuples)
                # TODO: proper format checks with schemas
                if isinstance(first_gold_tuple, dict):
                    if first_gold_tuple.get("paragraphs", None):
                        examples = read_json_object(gold_tuples)
                    elif first_gold_tuple.get("doc_annotation", None):
                        examples = []
                        for ex_dict in gold_tuples:
                            doc = ex_dict.get("doc", None)
                            if doc is None:
                                doc = ex_dict.get("text", None)
                            examples.append(Example.from_dict(ex_dict, doc=doc))

            elif file_name.endswith("msg"):
                text, ex_dict = srsly.read_msgpack(loc)
                examples = [Example.from_dict(ex_dict, doc=text)]
            else:
                supported = ("json", "jsonl", "msg")
                raise ValueError(Errors.E124.format(path=loc, formats=supported))
            try:
                for example in examples:
                    yield example
                    i += 1
                    if limit and i >= limit:
                        return
            except KeyError as e:
                msg = "Missing key {}".format(e)
                raise KeyError(Errors.E996.format(file=file_name, msg=msg))
            except UnboundLocalError as e:
                msg = "Unexpected document structure"
                raise ValueError(Errors.E996.format(file=file_name, msg=msg))

    @property
    def dev_examples(self):
        locs = (self.tmp_dir / "dev").iterdir()
        yield from self.read_examples(locs, limit=self.limit)

    @property
    def train_examples(self):
        locs = (self.tmp_dir / "train").iterdir()
        yield from self.read_examples(locs, limit=self.limit)

    def count_train(self):
        """Returns count of words in train examples"""
        n = 0
        i = 0
        for example in self.train_examples:
            n += len(example.token_annotation.words)
            if self.limit and i >= self.limit:
                break
            i += 1
        return n

    def train_dataset(self, nlp, gold_preproc=False, max_length=None,
                    noise_level=0.0, orth_variant_level=0.0,
                    ignore_misaligned=False):
        locs = list((self.tmp_dir / 'train').iterdir())
        random.shuffle(locs)
        train_examples = self.read_examples(locs, limit=self.limit)
        gold_examples = self.iter_gold_docs(nlp, train_examples, gold_preproc,
                                        max_length=max_length,
                                        noise_level=noise_level,
                                        orth_variant_level=orth_variant_level,
                                        make_projective=True,
                                        ignore_misaligned=ignore_misaligned)
        yield from gold_examples

    def train_dataset_without_preprocessing(self, nlp, gold_preproc=False,
                                            ignore_misaligned=False):
        examples = self.iter_gold_docs(nlp, self.train_examples,
                                       gold_preproc=gold_preproc,
                                       ignore_misaligned=ignore_misaligned)
        yield from examples

    def dev_dataset(self, nlp, gold_preproc=False, ignore_misaligned=False):
        examples = self.iter_gold_docs(nlp, self.dev_examples,
                                       gold_preproc=gold_preproc,
                                       ignore_misaligned=ignore_misaligned)
        yield from examples

    @classmethod
    def iter_gold_docs(cls, nlp, examples, gold_preproc, max_length=None,
                       noise_level=0.0, orth_variant_level=0.0,
                       make_projective=False, ignore_misaligned=False):
        """ Setting gold_preproc will result in creating a doc per sentence """
        for example in examples:
            if gold_preproc:
                example.doc = None
                split_examples = example.split_sents()
                example_golds = []
                for split_example in split_examples:
                    split_example_docs = cls._make_docs(nlp, split_example,
                            gold_preproc, noise_level=noise_level,
                            orth_variant_level=orth_variant_level)
                    split_example_golds = cls._make_golds(split_example_docs,
                            vocab=nlp.vocab, make_projective=make_projective,
                            ignore_misaligned=ignore_misaligned)
                    example_golds.extend(split_example_golds)
            else:
                example_docs = cls._make_docs(nlp, example,
                        gold_preproc, noise_level=noise_level,
                        orth_variant_level=orth_variant_level)
                example_golds = cls._make_golds(example_docs, vocab=nlp.vocab,
                        make_projective=make_projective,
                        ignore_misaligned=ignore_misaligned)
            for ex in example_golds:
                if ex.goldparse is not None:
                    if (not max_length) or len(ex.doc) < max_length:
                        yield ex

    @classmethod
    def _make_docs(cls, nlp, example, gold_preproc, noise_level=0.0, orth_variant_level=0.0):
        var_example = make_orth_variants(nlp, example, orth_variant_level=orth_variant_level)
        # gold_preproc is not used ?!
        if example.text is not None:
            var_text = add_noise(var_example.text, noise_level)
            var_doc = nlp.make_doc(var_text)
            var_example.doc = var_doc
        else:
            var_doc = Doc(nlp.vocab, words=add_noise(var_example.token_annotation.words, noise_level))
            var_example.doc = var_doc
        return [var_example]

    @classmethod
    def _make_golds(cls, examples, vocab=None, make_projective=False,
                    ignore_misaligned=False):
        filtered_examples = []
        for example in examples:
            gold_parses = example.get_gold_parses(vocab=vocab,
                    make_projective=make_projective,
                    ignore_misaligned=ignore_misaligned)
            assert len(gold_parses) == 1
            doc, gold = gold_parses[0]
            if doc:
                assert doc == example.doc
                example.goldparse = gold
                filtered_examples.append(example)
        return filtered_examples


def make_orth_variants(nlp, example, orth_variant_level=0.0):
    if random.random() >= orth_variant_level:
        return example
    if not example.token_annotation:
        return example
    raw = example.text
    if random.random() >= 0.5:
        lower = True
        if raw is not None:
            raw = raw.lower()
    ndsv = nlp.Defaults.single_orth_variants
    ndpv = nlp.Defaults.paired_orth_variants
    # modify words in paragraph_tuples
    variant_example = Example(doc=raw)
    token_annotation = example.token_annotation
    words = token_annotation.words
    tags = token_annotation.tags
    if not words or not tags:
       # add the unmodified annotation
        token_dict = token_annotation.to_dict()
        variant_example.set_token_annotation(**token_dict)
    else:
        if lower:
            words = [w.lower() for w in words]
        # single variants
        punct_choices = [random.choice(x["variants"]) for x in ndsv]
        for word_idx in range(len(words)):
            for punct_idx in range(len(ndsv)):
                if tags[word_idx] in ndsv[punct_idx]["tags"] \
                        and words[word_idx] in ndsv[punct_idx]["variants"]:
                    words[word_idx] = punct_choices[punct_idx]
        # paired variants
        punct_choices = [random.choice(x["variants"]) for x in ndpv]
        for word_idx in range(len(words)):
            for punct_idx in range(len(ndpv)):
                if tags[word_idx] in ndpv[punct_idx]["tags"] \
                        and words[word_idx] in itertools.chain.from_iterable(ndpv[punct_idx]["variants"]):
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
        variant_example.set_token_annotation(**token_dict)
    # modify raw to match variant_paragraph_tuples
    if raw is not None:
        variants = []
        for single_variants in ndsv:
            variants.extend(single_variants["variants"])
        for paired_variants in ndpv:
            variants.extend(list(itertools.chain.from_iterable(paired_variants["variants"])))
        # store variants in reverse length order to be able to prioritize
        # longer matches (e.g., "---" before "--")
        variants = sorted(variants, key=lambda x: len(x))
        variants.reverse()
        variant_raw = ""
        raw_idx = 0
        # add initial whitespace
        while raw_idx < len(raw) and re.match("\s", raw[raw_idx]):
            variant_raw += raw[raw_idx]
            raw_idx += 1
        for word in variant_example.token_annotation.words:
            match_found = False
            # add identical word
            if word not in variants and raw[raw_idx:].startswith(word):
                variant_raw += word
                raw_idx += len(word)
                match_found = True
            # add variant word
            else:
                for variant in variants:
                    if not match_found and \
                            raw[raw_idx:].startswith(variant):
                        raw_idx += len(variant)
                        variant_raw += word
                        match_found = True
            # something went wrong, abort
            # (add a warning message?)
            if not match_found:
                return example
            # add following whitespace
            while raw_idx < len(raw) and re.match("\s", raw[raw_idx]):
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


def read_json_object(json_corpus_section):
    """Take a list of JSON-formatted documents (e.g. from an already loaded
    training data file) and yield annotations in the GoldParse format.

    json_corpus_section (list): The data.
    YIELDS (Example): The reformatted data - one training example per paragraph
    """
    for json_doc in json_corpus_section:
        examples = json_to_examples(json_doc)
        for ex in examples:
            yield ex


def json_to_examples(doc):
    """Convert an item in the JSON-formatted training data to the format
    used by GoldParse.

    doc (dict): One entry in the training data.
    YIELDS (Example): The reformatted data - one training example per paragraph
    """
    paragraphs = []
    for paragraph in doc["paragraphs"]:
        example = Example(doc=paragraph.get("raw", None))
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
        example.set_token_annotation(ids=ids, words=words, tags=tags,
                pos=pos, morphs=morphs, lemmas=lemmas, heads=heads,
                deps=labels, entities=ner, sent_starts=sent_starts,
                brackets=brackets)
        example.set_doc_annotation(cats=cats)
        yield example


def read_json_file(loc, docs_filter=None, limit=None):
    loc = util.ensure_path(loc)
    if loc.is_dir():
        for filename in loc.iterdir():
            yield from read_json_file(loc / filename, limit=limit)
    else:
        for doc in _json_iterate(loc):
            if docs_filter is not None and not docs_filter(doc):
                continue
            for json_data in json_to_examples(doc):
                yield json_data


def _json_iterate(loc):
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


def iob_to_biluo(tags):
    out = []
    tags = list(tags)
    while tags:
        out.extend(_consume_os(tags))
        out.extend(_consume_ent(tags))
    return out


def biluo_to_iob(tags):
    out = []
    for tag in tags:
        tag = tag.replace("U-", "B-", 1).replace("L-", "I-", 1)
        out.append(tag)
    return out


def _consume_os(tags):
    while tags and tags[0] == "O":
        yield tags.pop(0)


def _consume_ent(tags):
    if not tags:
        return []
    tag = tags.pop(0)
    target_in = "I" + tag[1:]
    target_last = "L" + tag[1:]
    length = 1
    while tags and tags[0] in {target_in, target_last}:
        length += 1
        tags.pop(0)
    label = tag[2:]
    if length == 1:
        if len(label) == 0:
            raise ValueError(Errors.E177.format(tag=tag))
        return ["U-" + label]
    else:
        start = "B-" + label
        end = "L-" + label
        middle = [f"I-{label}" for _ in range(1, length - 1)]
        return [start] + middle + [end]


cdef class TokenAnnotation:
    def __init__(self, ids=None, words=None, tags=None, pos=None, morphs=None,
            lemmas=None, heads=None, deps=None, entities=None, sent_starts=None,
            brackets=None):
        self.ids = ids if ids else []
        self.words = words if words else []
        self.tags = tags if tags else []
        self.pos = pos if pos else []
        self.morphs = morphs if morphs else []
        self.lemmas = lemmas if lemmas else []
        self.heads = heads if heads else []
        self.deps = deps if deps else []
        self.entities = entities if entities else []
        self.sent_starts = sent_starts if sent_starts else []
        self.brackets = brackets if brackets else []

    @classmethod
    def from_dict(cls, token_dict):
        return cls(ids=token_dict.get("ids", None),
                   words=token_dict.get("words", None),
                   tags=token_dict.get("tags", None),
                   pos=token_dict.get("pos", None),
                   morphs=token_dict.get("morphs", None),
                   lemmas=token_dict.get("lemmas", None),
                   heads=token_dict.get("heads", None),
                   deps=token_dict.get("deps", None),
                   entities=token_dict.get("entities", None),
                   sent_starts=token_dict.get("sent_starts", None),
                   brackets=token_dict.get("brackets", None))

    def to_dict(self):
        return {"ids": self.ids,
                "words": self.words,
                "tags": self.tags,
                "pos": self.pos,
                "morphs": self.morphs,
                "lemmas": self.lemmas,
                "heads": self.heads,
                "deps": self.deps,
                "entities": self.entities,
                "sent_starts": self.sent_starts,
                "brackets": self.brackets}

    def get_id(self, i):
        return self.ids[i] if i < len(self.ids) else i

    def get_word(self, i):
        return self.words[i] if i < len(self.words) else ""

    def get_tag(self, i):
        return self.tags[i] if i < len(self.tags) else "-"

    def get_pos(self, i):
        return self.pos[i] if i < len(self.pos) else ""

    def get_morph(self, i):
        return self.morphs[i] if i < len(self.morphs) else ""

    def get_lemma(self, i):
        return self.lemmas[i] if i < len(self.lemmas) else ""

    def get_head(self, i):
        return self.heads[i] if i < len(self.heads) else i

    def get_dep(self, i):
        return self.deps[i] if i < len(self.deps) else ""

    def get_entity(self, i):
        return self.entities[i] if i < len(self.entities) else "-"

    def get_sent_start(self, i):
        return self.sent_starts[i] if i < len(self.sent_starts) else None


cdef class DocAnnotation:
    def __init__(self, cats=None, links=None):
        self.cats = cats if cats else {}
        self.links = links if links else {}

    @classmethod
    def from_dict(cls, doc_dict):
        return cls(cats=doc_dict.get("cats", None), links=doc_dict.get("links", None))

    def to_dict(self):
        return {"cats": self.cats, "links": self.links}


cdef class Example:
    def __init__(self, doc_annotation=None, token_annotation=None, doc=None,
                 goldparse=None):
        """ Doc can either be text, or an actual Doc """
        self.doc = doc
        self.doc_annotation = doc_annotation if doc_annotation else DocAnnotation()
        self.token_annotation = token_annotation if token_annotation else TokenAnnotation()
        self.goldparse = goldparse

    @classmethod
    def from_gold(cls, goldparse, doc=None):
        doc_annotation = DocAnnotation(cats=goldparse.cats, links=goldparse.links)
        token_annotation = goldparse.get_token_annotation()
        return cls(doc_annotation, token_annotation, doc)

    @classmethod
    def from_dict(cls, example_dict, doc=None):
        token_dict = example_dict["token_annotation"]
        token_annotation = TokenAnnotation.from_dict(token_dict)
        doc_dict = example_dict["doc_annotation"]
        doc_annotation = DocAnnotation.from_dict(doc_dict)
        return cls(doc_annotation, token_annotation, doc)

    def to_dict(self):
        """ Note that this method does NOT export the doc, only the annotations ! """
        token_dict = self.token_annotation.to_dict()
        doc_dict = self.doc_annotation.to_dict()
        return {"token_annotation": token_dict, "doc_annotation": doc_dict}

    @property
    def text(self):
        if self.doc is None:
            return None
        if isinstance(self.doc, Doc):
            return self.doc.text
        return self.doc

    @property
    def gold(self):
        if self.goldparse is None:
            doc, gold = self.get_gold_parses()[0]
            self.goldparse = gold
        return self.goldparse

    def set_token_annotation(self, ids=None, words=None, tags=None, pos=None,
                             morphs=None, lemmas=None, heads=None, deps=None,
                             entities=None, sent_starts=None, brackets=None):
        self.token_annotation = TokenAnnotation(ids=ids, words=words, tags=tags,
                            pos=pos, morphs=morphs, lemmas=lemmas, heads=heads,
                            deps=deps, entities=entities,
                            sent_starts=sent_starts, brackets=brackets)

    def set_doc_annotation(self, cats=None, links=None):
        if cats:
            self.doc_annotation.cats = cats
        if links:
            self.doc_annotation.links = links

    def split_sents(self):
        """ Split the token annotations into multiple Examples based on
        sent_starts and return a list of the new Examples"""
        s_example = Example(doc=None, doc_annotation=self.doc_annotation)
        s_ids, s_words, s_tags, s_pos, s_morphs = [], [], [], [], []
        s_lemmas, s_heads, s_deps, s_ents, s_sent_starts = [], [], [], [], []
        s_brackets = []
        sent_start_i = 0
        t = self.token_annotation
        split_examples = []
        for i in range(len(t.words)):
            if i > 0 and t.sent_starts[i] == 1:
                s_example.set_token_annotation(ids=s_ids,
                        words=s_words, tags=s_tags, pos=s_pos, morphs=s_morphs,
                        lemmas=s_lemmas, heads=s_heads, deps=s_deps,
                        entities=s_ents, sent_starts=s_sent_starts,
                        brackets=s_brackets)
                split_examples.append(s_example)
                s_example = Example(doc=None, doc_annotation=self.doc_annotation)
                s_ids, s_words, s_tags, s_pos, s_heads = [], [], [], [], []
                s_deps, s_ents, s_morphs, s_lemmas = [], [], [], []
                s_sent_starts, s_brackets = [], []
                sent_start_i = i
            s_ids.append(t.get_id(i))
            s_words.append(t.get_word(i))
            s_tags.append(t.get_tag(i))
            s_pos.append(t.get_pos(i))
            s_morphs.append(t.get_morph(i))
            s_lemmas.append(t.get_lemma(i))
            s_heads.append(t.get_head(i) - sent_start_i)
            s_deps.append(t.get_dep(i))
            s_ents.append(t.get_entity(i))
            s_sent_starts.append(t.get_sent_start(i))
            s_brackets.extend((b[0] - sent_start_i,
                               b[1] - sent_start_i, b[2])
                               for b in t.brackets if b[0] == i)
            i += 1
        s_example.set_token_annotation(ids=s_ids, words=s_words, tags=s_tags,
                pos=s_pos, morphs=s_morphs, lemmas=s_lemmas, heads=s_heads,
                deps=s_deps, entities=s_ents, sent_starts=s_sent_starts,
                brackets=s_brackets)
        split_examples.append(s_example)
        return split_examples


    def get_gold_parses(self, merge=True, vocab=None, make_projective=False,
                        ignore_misaligned=False):
        """Return a list of (doc, GoldParse) objects.
        If merge is set to True, keep all Token annotations as one big list."""
        d = self.doc_annotation
        # merge == do not modify Example
        if merge:
            t = self.token_annotation
            doc = self.doc
            if self.doc is None:
                if not vocab:
                    raise ValueError(Errors.E998)
                doc = Doc(vocab, words=t.words)
            try:
                gp = GoldParse.from_annotation(doc, d, t,
                                               make_projective=make_projective)
            except AlignmentError:
                if ignore_misaligned:
                    gp = None
                else:
                    raise
            return [(doc, gp)]
        # not merging: one GoldParse per sentence, defining docs with the words
        # from each sentence
        else:
            parses = []
            split_examples = self.split_sents()
            for split_example in split_examples:
                if not vocab:
                    raise ValueError(Errors.E998)
                split_doc = Doc(vocab, words=split_example.token_annotation.words)
                try:
                    gp = GoldParse.from_annotation(split_doc, d,
                            split_example.token_annotation,
                            make_projective=make_projective)
                except AlignmentError:
                    if ignore_misaligned:
                        gp = None
                    else:
                        raise
                if gp is not None:
                    parses.append((split_doc, gp))
            return parses

    @classmethod
    def to_example_objects(cls, examples, make_doc=None, keep_raw_text=False):
        """
        Return a list of Example objects, from a variety of input formats.
        make_doc needs to be provided when the examples contain text strings and keep_raw_text=False
        """
        if isinstance(examples, Example):
            return [examples]
        if isinstance(examples, tuple):
            examples = [examples]
        converted_examples = []
        for ex in examples:
            # convert string to Doc to Example
            if isinstance(ex, str):
                if keep_raw_text:
                    converted_examples.append(Example(doc=ex))
                else:
                    doc = make_doc(ex)
                    converted_examples.append(Example(doc=doc))
            # convert Doc to Example
            elif isinstance(ex, Doc):
                converted_examples.append(Example(doc=ex))
            # convert tuples to Example
            elif isinstance(ex, tuple) and len(ex) == 2:
                doc, gold = ex
                gold_dict = {}
                # convert string to Doc
                if isinstance(doc, str) and not keep_raw_text:
                    doc = make_doc(doc)
                # convert dict to GoldParse
                if isinstance(gold, dict):
                    gold_dict = gold
                    if doc is not None or gold.get("words", None) is not None:
                        gold = GoldParse(doc, **gold)
                    else:
                        gold = None
                if gold is not None:
                    converted_examples.append(Example.from_gold(goldparse=gold, doc=doc))
                else:
                    raise ValueError(Errors.E999.format(gold_dict=gold_dict))
            else:
                converted_examples.append(ex)
        return converted_examples


cdef class GoldParse:
    """Collection for training annotations.

    DOCS: https://spacy.io/api/goldparse
    """
    @classmethod
    def from_annotation(cls, doc, doc_annotation, token_annotation, make_projective=False):
        return cls(doc, words=token_annotation.words,
                   tags=token_annotation.tags,
                   pos=token_annotation.pos,
                   morphs=token_annotation.morphs,
                   lemmas=token_annotation.lemmas,
                   heads=token_annotation.heads,
                   deps=token_annotation.deps,
                   entities=token_annotation.entities,
                   sent_starts=token_annotation.sent_starts,
                   cats=doc_annotation.cats,
                   links=doc_annotation.links,
                   make_projective=make_projective)

    def get_token_annotation(self):
        ids = None
        if self.words:
            ids = list(range(len(self.words)))

        return TokenAnnotation(ids=ids, words=self.words, tags=self.tags,
                               pos=self.pos, morphs=self.morphs,
                               lemmas=self.lemmas, heads=self.heads,
                               deps=self.labels, entities=self.ner,
                               sent_starts=self.sent_starts)

    def __init__(self, doc, words=None, tags=None, pos=None, morphs=None,
                 lemmas=None, heads=None, deps=None, entities=None,
                 sent_starts=None, make_projective=False, cats=None,
                 links=None):
        """Create a GoldParse. The fields will not be initialized if len(doc) is zero.

        doc (Doc): The document the annotations refer to.
        words (iterable): A sequence of unicode word strings.
        tags (iterable): A sequence of strings, representing tag annotations.
        pos (iterable): A sequence of strings, representing UPOS annotations.
        morphs (iterable): A sequence of strings, representing morph
            annotations.
        lemmas (iterable): A sequence of strings, representing lemma
            annotations.
        heads (iterable): A sequence of integers, representing syntactic
            head offsets.
        deps (iterable): A sequence of strings, representing the syntactic
            relation types.
        entities (iterable): A sequence of named entity annotations, either as
            BILUO tag strings, or as `(start_char, end_char, label)` tuples,
            representing the entity positions.
        sent_starts (iterable): A sequence of sentence position tags, 1 for
            the first word in a sentence, 0 for all others.
        cats (dict): Labels for text classification. Each key in the dictionary
            may be a string or an int, or a `(start_char, end_char, label)`
            tuple, indicating that the label is applied to only part of the
            document (usually a sentence). Unlike entity annotations, label
            annotations can overlap, i.e. a single word can be covered by
            multiple labelled spans. The TextCategorizer component expects
            true examples of a label to have the value 1.0, and negative
            examples of a label to have the value 0.0. Labels not in the
            dictionary are treated as missing - the gradient for those labels
            will be zero.
        links (dict): A dict with `(start_char, end_char)` keys,
            and the values being dicts with kb_id:value entries,
            representing the external IDs in a knowledge base (KB)
            mapped to either 1.0 or 0.0, indicating positive and
            negative examples respectively.
        RETURNS (GoldParse): The newly constructed object.
        """
        self.mem = Pool()
        self.loss = 0
        self.length = len(doc)

        self.cats = {} if cats is None else dict(cats)
        self.links = {} if links is None else dict(links)

        # avoid allocating memory if the doc does not contain any tokens
        if self.length == 0:
            # set a minimal orig so that the scorer can score an empty doc
            self.orig = TokenAnnotation(ids=[])
        else:
            if not words:
                words = [token.text for token in doc]
            if not tags:
                tags = [None for _ in words]
            if not pos:
                pos = [None for _ in words]
            if not morphs:
                morphs = [None for _ in words]
            if not lemmas:
                lemmas = [None for _ in words]
            if not heads:
                heads = [None for _ in words]
            if not deps:
                deps = [None for _ in words]
            if not sent_starts:
                sent_starts = [None for _ in words]
            if entities is None:
                entities = ["-" for _ in words]
            elif len(entities) == 0:
                entities = ["O" for _ in words]
            else:
                # Translate the None values to '-', to make processing easier.
                # See Issue #2603
                entities = [(ent if ent is not None else "-") for ent in entities]
                if not isinstance(entities[0], str):
                    # Assume we have entities specified by character offset.
                    entities = biluo_tags_from_offsets(doc, entities)

            # These are filled by the tagger/parser/entity recogniser
            self.c.tags = <int*>self.mem.alloc(len(doc), sizeof(int))
            self.c.heads = <int*>self.mem.alloc(len(doc), sizeof(int))
            self.c.labels = <attr_t*>self.mem.alloc(len(doc), sizeof(attr_t))
            self.c.has_dep = <int*>self.mem.alloc(len(doc), sizeof(int))
            self.c.sent_start = <int*>self.mem.alloc(len(doc), sizeof(int))
            self.c.ner = <Transition*>self.mem.alloc(len(doc), sizeof(Transition))

            self.words = [None] * len(doc)
            self.tags = [None] * len(doc)
            self.pos = [None] * len(doc)
            self.morphs = [None] * len(doc)
            self.lemmas = [None] * len(doc)
            self.heads = [None] * len(doc)
            self.labels = [None] * len(doc)
            self.ner = [None] * len(doc)
            self.sent_starts = [None] * len(doc)

            # This needs to be done before we align the words
            if make_projective and heads is not None and deps is not None:
                heads, deps = nonproj.projectivize(heads, deps)

            # Do many-to-one alignment for misaligned tokens.
            # If we over-segment, we'll have one gold word that covers a sequence
            # of predicted words
            # If we under-segment, we'll have one predicted word that covers a
            # sequence of gold words.
            # If we "mis-segment", we'll have a sequence of predicted words covering
            # a sequence of gold words. That's many-to-many -- we don't do that.
            cost, i2j, j2i, i2j_multi, j2i_multi = align([t.orth_ for t in doc], words)

            self.cand_to_gold = [(j if j >= 0 else None) for j in i2j]
            self.gold_to_cand = [(i if i >= 0 else None) for i in j2i]

            self.orig = TokenAnnotation(ids=list(range(len(words))),
                    words=words, tags=tags, pos=pos, morphs=morphs,
                    lemmas=lemmas, heads=heads, deps=deps, entities=entities,
                    sent_starts=sent_starts, brackets=[])

            for i, gold_i in enumerate(self.cand_to_gold):
                if doc[i].text.isspace():
                    self.words[i] = doc[i].text
                    self.tags[i] = "_SP"
                    self.pos[i] = "SPACE"
                    self.morphs[i] = None
                    self.lemmas[i] = None
                    self.heads[i] = None
                    self.labels[i] = None
                    self.ner[i] = None
                    self.sent_starts[i] = 0
                if gold_i is None:
                    if i in i2j_multi:
                        self.words[i] = words[i2j_multi[i]]
                        self.tags[i] = tags[i2j_multi[i]]
                        self.pos[i] = pos[i2j_multi[i]]
                        self.morphs[i] = morphs[i2j_multi[i]]
                        self.lemmas[i] = lemmas[i2j_multi[i]]
                        self.sent_starts[i] = sent_starts[i2j_multi[i]]
                        is_last = i2j_multi[i] != i2j_multi.get(i+1)
                        is_first = i2j_multi[i] != i2j_multi.get(i-1)
                        # Set next word in multi-token span as head, until last
                        if not is_last:
                            self.heads[i] = i+1
                            self.labels[i] = "subtok"
                        else:
                            head_i = heads[i2j_multi[i]]
                            if head_i:
                                self.heads[i] = self.gold_to_cand[head_i]
                            self.labels[i] = deps[i2j_multi[i]]
                        # Now set NER...This is annoying because if we've split
                        # got an entity word split into two, we need to adjust the
                        # BILUO tags. We can't have BB or LL etc.
                        # Case 1: O -- easy.
                        ner_tag = entities[i2j_multi[i]]
                        if ner_tag == "O":
                            self.ner[i] = "O"
                        # Case 2: U. This has to become a B I* L sequence.
                        elif ner_tag.startswith("U-"):
                            if is_first:
                                self.ner[i] = ner_tag.replace("U-", "B-", 1)
                            elif is_last:
                                self.ner[i] = ner_tag.replace("U-", "L-", 1)
                            else:
                                self.ner[i] = ner_tag.replace("U-", "I-", 1)
                        # Case 3: L. If not last, change to I.
                        elif ner_tag.startswith("L-"):
                            if is_last:
                                self.ner[i] = ner_tag
                            else:
                                self.ner[i] = ner_tag.replace("L-", "I-", 1)
                        # Case 4: I. Stays correct
                        elif ner_tag.startswith("I-"):
                            self.ner[i] = ner_tag
                else:
                    self.words[i] = words[gold_i]
                    self.tags[i] = tags[gold_i]
                    self.pos[i] = pos[gold_i]
                    self.morphs[i] = morphs[gold_i]
                    self.lemmas[i] = lemmas[gold_i]
                    self.sent_starts[i] = sent_starts[gold_i]
                    if heads[gold_i] is None:
                        self.heads[i] = None
                    else:
                        self.heads[i] = self.gold_to_cand[heads[gold_i]]
                    self.labels[i] = deps[gold_i]
                    self.ner[i] = entities[gold_i]

            # Prevent whitespace that isn't within entities from being tagged as
            # an entity.
            for i in range(len(self.ner)):
                if self.tags[i] == "_SP":
                    prev_ner = self.ner[i-1] if i >= 1 else None
                    next_ner = self.ner[i+1] if (i+1) < len(self.ner) else None
                    if prev_ner == "O" or next_ner == "O":
                        self.ner[i] = "O"

            cycle = nonproj.contains_cycle(self.heads)
            if cycle is not None:
                raise ValueError(Errors.E069.format(cycle=cycle,
                    cycle_tokens=" ".join([f"'{self.words[tok_id]}'" for tok_id in cycle]),
                    doc_tokens=" ".join(words[:50])))

    def __len__(self):
        """Get the number of gold-standard tokens.

        RETURNS (int): The number of gold-standard tokens.
        """
        return self.length

    @property
    def is_projective(self):
        """Whether the provided syntactic annotations form a projective
        dependency tree.
        """
        return not nonproj.is_nonproj_tree(self.heads)


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


def biluo_tags_from_offsets(doc, entities, missing="O"):
    """Encode labelled spans into per-token tags, using the
    Begin/In/Last/Unit/Out scheme (BILUO).

    doc (Doc): The document that the entity offsets refer to. The output tags
        will refer to the token boundaries within the document.
    entities (iterable): A sequence of `(start, end, label)` triples. `start`
        and `end` should be character-offset integers denoting the slice into
        the original string.
    RETURNS (list): A list of unicode strings, describing the tags. Each tag
        string will be of the form either "", "O" or "{action}-{label}", where
        action is one of "B", "I", "L", "U". The string "-" is used where the
        entity offsets don't align with the tokenization in the `Doc` object.
        The training algorithm will view these as missing values. "O" denotes a
        non-entity token. "B" denotes the beginning of a multi-token entity,
        "I" the inside of an entity of three or more tokens, and "L" the end
        of an entity of two or more tokens. "U" denotes a single-token entity.

    EXAMPLE:
        >>> text = 'I like London.'
        >>> entities = [(len('I like '), len('I like London'), 'LOC')]
        >>> doc = nlp.tokenizer(text)
        >>> tags = biluo_tags_from_offsets(doc, entities)
        >>> assert tags == ["O", "O", 'U-LOC', "O"]
    """
    # Ensure no overlapping entity labels exist
    tokens_in_ents = {}

    starts = {token.idx: token.i for token in doc}
    ends = {token.idx + len(token): token.i for token in doc}
    biluo = ["-" for _ in doc]
    # Handle entity cases
    for start_char, end_char, label in entities:
        for token_index in range(start_char, end_char):
            if token_index in tokens_in_ents.keys():
                raise ValueError(Errors.E103.format(
                    span1=(tokens_in_ents[token_index][0],
                            tokens_in_ents[token_index][1],
                            tokens_in_ents[token_index][2]),
                    span2=(start_char, end_char, label)))
            tokens_in_ents[token_index] = (start_char, end_char, label)

        start_token = starts.get(start_char)
        end_token = ends.get(end_char)
        # Only interested if the tokenization is correct
        if start_token is not None and end_token is not None:
            if start_token == end_token:
                biluo[start_token] = f"U-{label}"
            else:
                biluo[start_token] = f"B-{label}"
                for i in range(start_token+1, end_token):
                    biluo[i] = f"I-{label}"
                biluo[end_token] = f"L-{label}"
    # Now distinguish the O cases from ones where we miss the tokenization
    entity_chars = set()
    for start_char, end_char, label in entities:
        for i in range(start_char, end_char):
            entity_chars.add(i)
    for token in doc:
        for i in range(token.idx, token.idx + len(token)):
            if i in entity_chars:
                break
        else:
            biluo[token.i] = missing
    return biluo


def spans_from_biluo_tags(doc, tags):
    """Encode per-token tags following the BILUO scheme into Span object, e.g.
    to overwrite the doc.ents.

    doc (Doc): The document that the BILUO tags refer to.
    entities (iterable): A sequence of BILUO tags with each tag describing one
        token. Each tags string will be of the form of either "", "O" or
        "{action}-{label}", where action is one of "B", "I", "L", "U".
    RETURNS (list): A sequence of Span objects.
    """
    token_offsets = tags_to_entities(tags)
    spans = []
    for label, start_idx, end_idx in token_offsets:
        span = Span(doc, start_idx, end_idx + 1, label=label)
        spans.append(span)
    return spans


def offsets_from_biluo_tags(doc, tags):
    """Encode per-token tags following the BILUO scheme into entity offsets.

    doc (Doc): The document that the BILUO tags refer to.
    entities (iterable): A sequence of BILUO tags with each tag describing one
        token. Each tags string will be of the form of either "", "O" or
        "{action}-{label}", where action is one of "B", "I", "L", "U".
    RETURNS (list): A sequence of `(start, end, label)` triples. `start` and
        `end` will be character-offset integers denoting the slice into the
        original string.
    """
    spans = spans_from_biluo_tags(doc, tags)
    return [(span.start_char, span.end_char, span.label_) for span in spans]


def is_punct_label(label):
    return label == "P" or label.lower() == "punct"

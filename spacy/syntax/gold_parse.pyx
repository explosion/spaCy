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

from .. import util
from . import nonproj
from ..tokens import Doc, Span
from ..errors import Errors, AlignmentError, Warnings
from ..gold.annotation import TokenAnnotation
from ..gold.iob_utils import offsets_from_biluo_tags, biluo_tags_from_offsets
from ..gold.align import align


punct_re = re.compile(r"\W")

def is_punct_label(label):
    return label == "P" or label.lower() == "punct"


def get_parses_from_example(
    example, merge=True, vocab=None, make_projective=True, ignore_misaligned=False
):
    """Return a list of (doc, GoldParse) objects.
    If merge is set to True, keep all Token annotations as one big list."""
    # merge == do not modify Example
    if merge:
        examples = [example]
    else:
        # not merging: one GoldParse per sentence, defining docs with the words
        # from each sentence
        examples = eg.split_sents()
    outputs = []
    for eg in examples:
        eg_dict = eg.to_dict()
        try:
            gp = GoldParse.from_annotation(
                eg.predicted,
                eg_dict["doc_annotation"],
                eg_dict["token_annotation"],
                make_projective=make_projective
            )
        except AlignmentError:
            if ignore_misaligned:
                gp = None
            else:
                raise
        outputs.append((eg.predicted, gp))
    return outputs


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

        # temporary doc for aligning entity annotation
        entdoc = None

        # avoid allocating memory if the doc does not contain any tokens
        if self.length == 0:
            self.words = []
            self.tags = []
            self.heads = []
            self.labels = []
            self.ner = []
            self.morphs = []
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
                    # Create a temporary Doc corresponding to provided words
                    # (to preserve gold tokenization) and text (to preserve
                    # character offsets).
                    entdoc_words, entdoc_spaces = util.get_words_and_spaces(words, doc.text)
                    entdoc = Doc(doc.vocab, words=entdoc_words, spaces=entdoc_spaces)
                    entdoc_entities = biluo_tags_from_offsets(entdoc, entities)
                    # There may be some additional whitespace tokens in the
                    # temporary doc, so check that the annotations align with
                    # the provided words while building a list of BILUO labels.
                    entities = []
                    words_offset = 0
                    for i in range(len(entdoc_words)):
                        if words[i + words_offset] == entdoc_words[i]:
                            entities.append(entdoc_entities[i])
                        else:
                            words_offset -= 1
                    if len(entities) != len(words):
                        warnings.warn(Warnings.W029.format(text=doc.text))
                        entities = ["-" for _ in words]

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
            if make_projective and any(heads) and any(deps) :
                heads, deps = nonproj.projectivize(heads, deps)

            # Do many-to-one alignment for misaligned tokens.
            # If we over-segment, we'll have one gold word that covers a sequence
            # of predicted words
            # If we under-segment, we'll have one predicted word that covers a
            # sequence of gold words.
            # If we "mis-segment", we'll have a sequence of predicted words covering
            # a sequence of gold words. That's many-to-many -- we don't do that
            # except for NER spans where the start and end can be aligned.
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
                        # Set next word in multi-token span as head, until last
                        if not is_last:
                            self.heads[i] = i+1
                            self.labels[i] = "subtok"
                        else:
                            head_i = heads[i2j_multi[i]]
                            if head_i:
                                self.heads[i] = self.gold_to_cand[head_i]
                            self.labels[i] = deps[i2j_multi[i]]
                        ner_tag = entities[i2j_multi[i]]
                        # Assign O/- for many-to-one O/- NER tags
                        if ner_tag in ("O", "-"):
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
            # Assign O/- for one-to-many O/- NER tags
            for j, cand_j in enumerate(self.gold_to_cand):
                if cand_j is None:
                    if j in j2i_multi:
                        i = j2i_multi[j]
                        ner_tag = entities[j]
                        if ner_tag in ("O", "-"):
                            self.ner[i] = ner_tag

            # If there is entity annotation and some tokens remain unaligned,
            # align all entities at the character level to account for all
            # possible token misalignments within the entity spans
            if any([e not in ("O", "-") for e in entities]) and None in self.ner:
                # If the temporary entdoc wasn't created above, initialize it
                if not entdoc:
                    entdoc_words, entdoc_spaces = util.get_words_and_spaces(words, doc.text)
                    entdoc = Doc(doc.vocab, words=entdoc_words, spaces=entdoc_spaces)
                # Get offsets based on gold words and BILUO entities
                entdoc_offsets = offsets_from_biluo_tags(entdoc, entities)
                aligned_offsets = []
                aligned_spans = []
                # Filter offsets to identify those that align with doc tokens
                for offset in entdoc_offsets:
                    span = doc.char_span(offset[0], offset[1])
                    if span and not span.text.isspace():
                        aligned_offsets.append(offset)
                        aligned_spans.append(span)
                # Convert back to BILUO for doc tokens and assign NER for all
                # aligned spans
                biluo_tags = biluo_tags_from_offsets(doc, aligned_offsets, missing=None)
                for span in aligned_spans:
                    for i in range(span.start, span.end):
                        self.ner[i] = biluo_tags[i]

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

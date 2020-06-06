from .annotation import TokenAnnotation, DocAnnotation
from ..errors import Errors, AlignmentError
from ..tokens import Doc

# We're hoping to kill this GoldParse dependency but for now match semantics.
from ..syntax.gold_parse import GoldParse


class Example:
    def __init__(
        self, doc_annotation=None, token_annotation=None, doc=None, goldparse=None
    ):
        """ Doc can either be text, or an actual Doc """
        self.doc = doc
        self.doc_annotation = doc_annotation if doc_annotation else DocAnnotation()
        self.token_annotation = (
            token_annotation if token_annotation else TokenAnnotation()
        )
        self.goldparse = goldparse

    @classmethod
    def from_gold(cls, goldparse, doc=None):
        doc_annotation = DocAnnotation(cats=goldparse.cats, links=goldparse.links)
        token_annotation = goldparse.get_token_annotation()
        return cls(doc_annotation, token_annotation, doc)

    @classmethod
    def from_dict(cls, example_dict, doc=None):
        token_dict = example_dict.get("token_annotation", {})
        token_annotation = TokenAnnotation.from_dict(token_dict)
        doc_dict = example_dict.get("doc_annotation", {})
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

    def set_token_annotation(
        self,
        ids=None,
        words=None,
        tags=None,
        pos=None,
        morphs=None,
        lemmas=None,
        heads=None,
        deps=None,
        entities=None,
        sent_starts=None,
        brackets=None,
    ):
        self.token_annotation = TokenAnnotation(
            ids=ids,
            words=words,
            tags=tags,
            pos=pos,
            morphs=morphs,
            lemmas=lemmas,
            heads=heads,
            deps=deps,
            entities=entities,
            sent_starts=sent_starts,
            brackets=brackets,
        )

    def set_doc_annotation(self, cats=None, links=None):
        if cats:
            self.doc_annotation.cats = cats
        if links:
            self.doc_annotation.links = links

    def split_sents(self):
        """ Split the token annotations into multiple Examples based on
        sent_starts and return a list of the new Examples"""
        if not self.token_annotation.words:
            return [self]
        s_example = Example(doc=None, doc_annotation=self.doc_annotation)
        s_ids, s_words, s_tags, s_pos, s_morphs = [], [], [], [], []
        s_lemmas, s_heads, s_deps, s_ents, s_sent_starts = [], [], [], [], []
        s_brackets = []
        sent_start_i = 0
        t = self.token_annotation
        split_examples = []
        for i in range(len(t.words)):
            if i > 0 and t.sent_starts[i] == 1:
                s_example.set_token_annotation(
                    ids=s_ids,
                    words=s_words,
                    tags=s_tags,
                    pos=s_pos,
                    morphs=s_morphs,
                    lemmas=s_lemmas,
                    heads=s_heads,
                    deps=s_deps,
                    entities=s_ents,
                    sent_starts=s_sent_starts,
                    brackets=s_brackets,
                )
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
            for b_end, b_label in t.brackets_by_start.get(i, []):
                s_brackets.append((i - sent_start_i, b_end - sent_start_i, b_label))
            i += 1
        s_example.set_token_annotation(
            ids=s_ids,
            words=s_words,
            tags=s_tags,
            pos=s_pos,
            morphs=s_morphs,
            lemmas=s_lemmas,
            heads=s_heads,
            deps=s_deps,
            entities=s_ents,
            sent_starts=s_sent_starts,
            brackets=s_brackets,
        )
        split_examples.append(s_example)
        return split_examples

    def get_gold_parses(
        self, merge=True, vocab=None, make_projective=False, ignore_misaligned=False
    ):
        """Return a list of (doc, GoldParse) objects.
        If merge is set to True, keep all Token annotations as one big list."""
        d = self.doc_annotation
        # merge == do not modify Example
        if merge:
            t = self.token_annotation
            doc = self.doc
            if doc is None or not isinstance(doc, Doc):
                if not vocab:
                    raise ValueError(Errors.E998)
                doc = Doc(vocab, words=t.words)
            try:
                gp = GoldParse.from_annotation(
                    doc, d, t, make_projective=make_projective
                )
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
                    gp = GoldParse.from_annotation(
                        split_doc,
                        d,
                        split_example.token_annotation,
                        make_projective=make_projective,
                    )
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
            if isinstance(ex, Example):
                converted_examples.append(ex)
            # convert string to Doc to Example
            elif isinstance(ex, str):
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
                    converted_examples.append(
                        Example.from_gold(goldparse=gold, doc=doc)
                    )
                else:
                    raise ValueError(Errors.E999.format(gold_dict=gold_dict))
            else:
                converted_examples.append(ex)
        return converted_examples

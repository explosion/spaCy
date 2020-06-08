from .annotation import TokenAnnotation, DocAnnotation
from .align import Alignment
from ..errors import Errors, AlignmentError
from ..tokens import Doc


class Example:
    def __init__(self, doc=None, doc_annotation=None, token_annotation=None):
        """ Doc can either be text, or an actual Doc """
        self.doc = doc
        self.doc_annotation = doc_annotation if doc_annotation else DocAnnotation()
        self.token_annotation = (
            token_annotation if token_annotation else TokenAnnotation()
        )
        self._alignment = None

    def _deprecated_get_gold(self, make_projective=False):
        from ..syntax.gold_parse import get_parses_from_example

        _, gold = get_parses_from_example(self, make_projective=make_projective)[0]
        return gold

    @classmethod
    def from_dict(cls, example_dict, doc=None):
        if example_dict is None:
            raise ValueError("Example.from_dict expected dict, received None")
        # TODO: This is ridiculous...
        token_dict = example_dict.get("token_annotation", {})
        doc_dict = example_dict.get("doc_annotation", {})
        for key, value in example_dict.items():
            if key in ("token_annotation", "doc_annotation"):
                pass
            elif key in ("cats", "links"):
                doc_dict[key] = value
            else:
                token_dict[key] = value
        token_annotation = TokenAnnotation.from_dict(token_dict)
        doc_annotation = DocAnnotation.from_dict(doc_dict)
        return cls(
            doc=doc, doc_annotation=doc_annotation, token_annotation=token_annotation
        )

    @property
    def alignment(self):
        if self._alignment is None:
            if self.doc is None:
                return None
            spacy_words = [token.orth_ for token in self.doc]
            gold_words = self.token_annotation.words
            if gold_words == []:
                gold_words = spacy_words
            self._alignment = Alignment(spacy_words, gold_words)
        return self._alignment

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

    def get_aligned(self, field):
        """Return an aligned array for a token annotation field."""
        if self.doc is None:
            return self.token_annotation.get_field(field)
        doc = self.doc
        if field == "word":
            return [token.orth_ for token in doc]
        gold_values = self.token_annotation.get_field(field)
        alignment = self.alignment
        i2j_multi = alignment.i2j_multi
        gold_to_cand = alignment.gold_to_cand
        cand_to_gold = alignment.cand_to_gold

        output = []
        for i, gold_i in enumerate(cand_to_gold):
            if doc[i].text.isspace():
                output.append(None)
            elif gold_i is None:
                if i in i2j_multi:
                    output.append(gold_values[i2j_multi[i]])
                else:
                    output.append(None)
            else:
                output.append(gold_values[gold_i])
        return output

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
            # convert tuples to Example
            elif isinstance(ex, tuple) and len(ex) == 2:
                doc, gold = ex
                # convert string to Doc
                if isinstance(doc, str) and not keep_raw_text:
                    doc = make_doc(doc)
                converted_examples.append(Example.from_dict(gold, doc=doc))
            # convert Doc to Example
            elif isinstance(ex, Doc):
                converted_examples.append(Example(doc=ex))
            else:
                converted_examples.append(ex)
        return converted_examples

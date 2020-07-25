# cython: infer_types=True, profile=True, binding=True
import numpy
import srsly

from thinc.api import Model, set_dropout_rate, SequenceCategoricalCrossentropy, Config
import warnings

from ..tokens.doc cimport Doc
from ..morphology cimport Morphology
from ..vocab cimport Vocab

from .pipe import Pipe, deserialize_config
from ..language import Language
from ..attrs import POS, ID
from ..parts_of_speech import X
from ..errors import Errors, TempErrors, Warnings
from ..scorer import Scorer
from .. import util


default_model_config = """
[model]
@architectures = "spacy.Tagger.v1"

[model.tok2vec]
@architectures = "spacy.HashEmbedCNN.v1"
pretrained_vectors = null
width = 96
depth = 4
embed_size = 2000
window_size = 1
maxout_pieces = 3
subword_features = true
dropout = null
"""
DEFAULT_TAGGER_MODEL = Config().from_str(default_model_config)["model"]


@Language.factory(
    "tagger",
    assigns=["token.tag"],
    default_config={"model": DEFAULT_TAGGER_MODEL, "set_morphology": False}
)
def make_tagger(nlp: Language, name: str, model: Model, set_morphology: bool):
    return Tagger(nlp.vocab, model, name, set_morphology=set_morphology)


class Tagger(Pipe):
    """Pipeline component for part-of-speech tagging.

    DOCS: https://spacy.io/api/tagger
    """
    def __init__(self, vocab, model, name="tagger", *, set_morphology=False):
        self.vocab = vocab
        self.model = model
        self.name = name
        self._rehearsal_model = None
        cfg = {"set_morphology": set_morphology}
        self.cfg = dict(sorted(cfg.items()))

    @property
    def labels(self):
        return tuple(self.vocab.morphology.tag_names)

    def __call__(self, doc):
        tags = self.predict([doc])
        self.set_annotations([doc], tags)
        return doc

    def pipe(self, stream, batch_size=128):
        for docs in util.minibatch(stream, size=batch_size):
            tag_ids = self.predict(docs)
            self.set_annotations(docs, tag_ids)
            yield from docs

    def predict(self, docs):
        if not any(len(doc) for doc in docs):
            # Handle cases where there are no tokens in any docs.
            n_labels = len(self.labels)
            guesses = [self.model.ops.alloc((0, n_labels)) for doc in docs]
            assert len(guesses) == len(docs)
            return guesses
        scores = self.model.predict(docs)
        assert len(scores) == len(docs), (len(scores), len(docs))
        guesses = self._scores2guesses(scores)
        assert len(guesses) == len(docs)
        return guesses

    def _scores2guesses(self, scores):
        guesses = []
        for doc_scores in scores:
            doc_guesses = doc_scores.argmax(axis=1)
            if not isinstance(doc_guesses, numpy.ndarray):
                doc_guesses = doc_guesses.get()
            guesses.append(doc_guesses)
        return guesses

    def set_annotations(self, docs, batch_tag_ids):
        if isinstance(docs, Doc):
            docs = [docs]
        cdef Doc doc
        cdef int idx = 0
        cdef Vocab vocab = self.vocab
        assign_morphology = self.cfg.get("set_morphology", True)
        for i, doc in enumerate(docs):
            doc_tag_ids = batch_tag_ids[i]
            if hasattr(doc_tag_ids, "get"):
                doc_tag_ids = doc_tag_ids.get()
            for j, tag_id in enumerate(doc_tag_ids):
                # Don't clobber preset POS tags
                if doc.c[j].tag == 0:
                    if doc.c[j].pos == 0 and assign_morphology:
                        # Don't clobber preset lemmas
                        lemma = doc.c[j].lemma
                        vocab.morphology.assign_tag_id(&doc.c[j], tag_id)
                        if lemma != 0 and lemma != doc.c[j].lex.orth:
                            doc.c[j].lemma = lemma
                    else:
                        doc.c[j].tag = self.vocab.strings[self.labels[tag_id]]
                idx += 1
            doc.is_tagged = True

    def update(self, examples, *, drop=0., sgd=None, losses=None, set_annotations=False):
        if losses is None:
            losses = {}
        losses.setdefault(self.name, 0.0)

        try:
            if not any(len(eg.predicted) if eg.predicted else 0 for eg in examples):
                # Handle cases where there are no tokens in any docs.
                return
        except AttributeError:
            types = set([type(eg) for eg in examples])
            raise TypeError(Errors.E978.format(name="Tagger", method="update", types=types))
        set_dropout_rate(self.model, drop)
        tag_scores, bp_tag_scores = self.model.begin_update(
            [eg.predicted for eg in examples])
        for sc in tag_scores:
            if self.model.ops.xp.isnan(sc.sum()):
                raise ValueError("nan value in scores")
        loss, d_tag_scores = self.get_loss(examples, tag_scores)
        bp_tag_scores(d_tag_scores)
        if sgd not in (None, False):
            self.model.finish_update(sgd)

        losses[self.name] += loss
        if set_annotations:
            docs = [eg.predicted for eg in examples]
            self.set_annotations(docs, self._scores2guesses(tag_scores))
        return losses

    def rehearse(self, examples, drop=0., sgd=None, losses=None):
        """Perform a 'rehearsal' update, where we try to match the output of
        an initial model.
        """
        try:
            docs = [eg.predicted for eg in examples]
        except AttributeError:
            types = set([type(eg) for eg in examples])
            raise TypeError(Errors.E978.format(name="Tagger", method="rehearse", types=types))
        if self._rehearsal_model is None:
            return
        if not any(len(doc) for doc in docs):
            # Handle cases where there are no tokens in any docs.
            return
        set_dropout_rate(self.model, drop)
        guesses, backprop = self.model.begin_update(docs)
        target = self._rehearsal_model(examples)
        gradient = guesses - target
        backprop(gradient)
        self.model.finish_update(sgd)
        if losses is not None:
            losses.setdefault(self.name, 0.0)
            losses[self.name] += (gradient**2).sum()

    def get_loss(self, examples, scores):
        loss_func = SequenceCategoricalCrossentropy(names=self.labels, normalize=False)
        truths = [eg.get_aligned("tag", as_string=True) for eg in examples]
        d_scores, loss = loss_func(scores, truths)
        if self.model.ops.xp.isnan(loss):
            raise ValueError("nan value when computing loss")
        return float(loss), d_scores

    def begin_training(self, get_examples=lambda: [], pipeline=None, sgd=None):
        lemma_tables = ["lemma_rules", "lemma_index", "lemma_exc", "lemma_lookup"]
        if not any(table in self.vocab.lookups for table in lemma_tables):
            warnings.warn(Warnings.W022)
        lexeme_norms = self.vocab.lookups.get_table("lexeme_norm", {})
        if len(lexeme_norms) == 0 and self.vocab.lang in util.LEXEME_NORM_LANGS:
            langs = ", ".join(util.LEXEME_NORM_LANGS)
            warnings.warn(Warnings.W033.format(model="part-of-speech tagger", langs=langs))
        orig_tag_map = dict(self.vocab.morphology.tag_map)
        new_tag_map = {}
        for example in get_examples():
            try:
                y = example.y
            except AttributeError:
                raise TypeError(Errors.E978.format(name="Tagger", method="begin_training", types=type(example)))
            for token in y:
                tag = token.tag_
                if tag in orig_tag_map:
                    new_tag_map[tag] = orig_tag_map[tag]
                else:
                    new_tag_map[tag] = {POS: X}

        cdef Vocab vocab = self.vocab
        if new_tag_map:
            if "_SP" in orig_tag_map:
                new_tag_map["_SP"] = orig_tag_map["_SP"]
            vocab.morphology.load_tag_map(new_tag_map)
        self.set_output(len(self.labels))
        doc_sample = [Doc(self.vocab, words=["hello", "world"])]
        if pipeline is not None:
            for name, component in pipeline:
                if component is self:
                    break
                if hasattr(component, "pipe"):
                    doc_sample = list(component.pipe(doc_sample))
                else:
                    doc_sample = [component(doc) for doc in doc_sample]
        self.model.initialize(X=doc_sample)
        # Get batch of example docs, example outputs to call begin_training().
        # This lets the model infer shapes.
        util.link_vectors_to_models(self.vocab)
        if sgd is None:
            sgd = self.create_optimizer()
        return sgd

    def add_label(self, label, values=None):
        if not isinstance(label, str):
            raise ValueError(Errors.E187)
        if label in self.labels:
            return 0
        if self.model.has_dim("nO"):
            # Here's how the model resizing will work, once the
            # neuron-to-tag mapping is no longer controlled by
            # the Morphology class, which sorts the tag names.
            # The sorting makes adding labels difficult.
            # smaller = self.model._layers[-1]
            # larger = Softmax(len(self.labels)+1, smaller.nI)
            # copy_array(larger.W[:smaller.nO], smaller.W)
            # copy_array(larger.b[:smaller.nO], smaller.b)
            # self.model._layers[-1] = larger
            raise ValueError(TempErrors.T003)
        tag_map = dict(self.vocab.morphology.tag_map)
        if values is None:
            values = {POS: "X"}
        tag_map[label] = values
        self.vocab.morphology.load_tag_map(tag_map)
        return 1

    def use_params(self, params):
        with self.model.use_params(params):
            yield

    def score(self, examples, **kwargs):
        scores = {}
        scores.update(Scorer.score_token_attr(examples, "tag", **kwargs))
        scores.update(Scorer.score_token_attr(examples, "pos", **kwargs))
        scores.update(Scorer.score_token_attr(examples, "lemma", **kwargs))
        return scores

    def to_bytes(self, exclude=tuple()):
        serialize = {}
        serialize["model"] = self.model.to_bytes
        serialize["vocab"] = self.vocab.to_bytes
        serialize["cfg"] = lambda: srsly.json_dumps(self.cfg)
        tag_map = dict(sorted(self.vocab.morphology.tag_map.items()))
        serialize["tag_map"] = lambda: srsly.msgpack_dumps(tag_map)
        morph_rules = dict(self.vocab.morphology.exc)
        serialize["morph_rules"] = lambda: srsly.msgpack_dumps(morph_rules)
        return util.to_bytes(serialize, exclude)

    def from_bytes(self, bytes_data, exclude=tuple()):
        def load_model(b):
            try:
                self.model.from_bytes(b)
            except AttributeError:
                raise ValueError(Errors.E149)

        def load_tag_map(b):
            tag_map = srsly.msgpack_loads(b)
            self.vocab.morphology.load_tag_map(tag_map)

        def load_morph_rules(b):
            morph_rules = srsly.msgpack_loads(b)
            self.vocab.morphology.load_morph_exceptions(morph_rules)

        self.vocab.morphology = Morphology(self.vocab.strings, dict(),
            lemmatizer=self.vocab.morphology.lemmatizer)

        deserialize = {
            "vocab": lambda b: self.vocab.from_bytes(b),
            "tag_map": load_tag_map,
            "morph_rules": load_morph_rules,
            "cfg": lambda b: self.cfg.update(srsly.json_loads(b)),
            "model": lambda b: load_model(b),
        }
        util.from_bytes(bytes_data, deserialize, exclude)
        return self

    def to_disk(self, path, exclude=tuple()):
        tag_map = dict(sorted(self.vocab.morphology.tag_map.items()))
        morph_rules = dict(self.vocab.morphology.exc)
        serialize = {
            "vocab": lambda p: self.vocab.to_disk(p),
            "tag_map": lambda p: srsly.write_msgpack(p, tag_map),
            "morph_rules": lambda p: srsly.write_msgpack(p, morph_rules),
            "model": lambda p: self.model.to_disk(p),
            "cfg": lambda p: srsly.write_json(p, self.cfg),
        }
        util.to_disk(path, serialize, exclude)

    def from_disk(self, path, exclude=tuple()):
        def load_model(p):
            with p.open("rb") as file_:
                try:
                    self.model.from_bytes(file_.read())
                except AttributeError:
                    raise ValueError(Errors.E149)

        def load_tag_map(p):
            tag_map = srsly.read_msgpack(p)
            self.vocab.morphology.load_tag_map(tag_map)

        def load_morph_rules(p):
            morph_rules = srsly.read_msgpack(p)
            self.vocab.morphology.load_morph_exceptions(morph_rules)

        self.vocab.morphology = Morphology(self.vocab.strings, dict(),
            lemmatizer=self.vocab.morphology.lemmatizer)

        deserialize = {
            "vocab": lambda p: self.vocab.from_disk(p),
            "cfg": lambda p: self.cfg.update(deserialize_config(p)),
            "tag_map": load_tag_map,
            "morph_rules": load_morph_rules,
            "model": load_model,
        }
        util.from_disk(path, deserialize, exclude)
        return self

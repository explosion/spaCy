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
    default_config={"model": DEFAULT_TAGGER_MODEL, "set_morphology": False},
    scores=["tag_acc", "pos_acc", "lemma_acc"],
    default_score_weights={"tag_acc": 1.0},
)
def make_tagger(nlp: Language, name: str, model: Model, set_morphology: bool):
    return Tagger(nlp.vocab, model, name, set_morphology=set_morphology)


class Tagger(Pipe):
    """Pipeline component for part-of-speech tagging.

    DOCS: https://spacy.io/api/tagger
    """
    def __init__(self, vocab, model, name="tagger", *, set_morphology=False):
        """Initialize a part-of-speech tagger.

        vocab (Vocab): The shared vocabulary.
        model (thinc.api.Model): The Thinc Model powering the pipeline component.
        name (str): The component instance name, used to add entries to the
            losses during training.
        set_morphology (bool): Whether to set morphological features.

        DOCS: https://spacy.io/api/tagger#init
        """
        self.vocab = vocab
        self.model = model
        self.name = name
        self._rehearsal_model = None
        cfg = {"set_morphology": set_morphology}
        self.cfg = dict(sorted(cfg.items()))

    @property
    def labels(self):
        """The labels currently added to the component. Note that even for a
        blank component, this will always include the built-in coarse-grained
        part-of-speech tags by default.

        RETURNS (Tuple[str]): The labels.

        DOCS: https://spacy.io/api/tagger#labels
        """
        return tuple(self.vocab.morphology.tag_names)

    def __call__(self, doc):
        """Apply the pipe to a Doc.

        doc (Doc): The document to process.
        RETURNS (Doc): The processed Doc.

        DOCS: https://spacy.io/api/tagger#call
        """
        tags = self.predict([doc])
        self.set_annotations([doc], tags)
        return doc

    def pipe(self, stream, *, batch_size=128):
        """Apply the pipe to a stream of documents. This usually happens under
        the hood when the nlp object is called on a text and all components are
        applied to the Doc.

        stream (Iterable[Doc]): A stream of documents.
        batch_size (int): The number of documents to buffer.
        YIELDS (Doc): Processed documents in order.

        DOCS: https://spacy.io/api/tagger#pipe
        """
        for docs in util.minibatch(stream, size=batch_size):
            tag_ids = self.predict(docs)
            self.set_annotations(docs, tag_ids)
            yield from docs

    def predict(self, docs):
        """Apply the pipeline's model to a batch of docs, without modifying them.

        docs (Iterable[Doc]): The documents to predict.
        RETURNS: The models prediction for each document.

        DOCS: https://spacy.io/api/tagger#predict
        """
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
        """Modify a batch of documents, using pre-computed scores.

        docs (Iterable[Doc]): The documents to modify.
        batch_tag_ids: The IDs to set, produced by Tagger.predict.

        DOCS: https://spacy.io/api/tagger#set_annotations
        """
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
        """Learn from a batch of documents and gold-standard information,
        updating the pipe's model. Delegates to predict and get_loss.

        examples (Iterable[Example]): A batch of Example objects.
        drop (float): The dropout rate.
        set_annotations (bool): Whether or not to update the Example objects
            with the predictions.
        sgd (thinc.api.Optimizer): The optimizer.
        losses (Dict[str, float]): Optional record of the loss during training.
            Updated using the component name as the key.
        RETURNS (Dict[str, float]): The updated losses dictionary.

        DOCS: https://spacy.io/api/tagger#update
        """
        if losses is None:
            losses = {}
        losses.setdefault(self.name, 0.0)
        try:
            if not any(len(eg.predicted) if eg.predicted else 0 for eg in examples):
                # Handle cases where there are no tokens in any docs.
                return
        except AttributeError:
            types = set([type(eg) for eg in examples])
            raise TypeError(Errors.E978.format(name="Tagger", method="update", types=types)) from None
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

    def rehearse(self, examples, *, drop=0., sgd=None, losses=None):
        """Perform a "rehearsal" update from a batch of data. Rehearsal updates
        teach the current model to make predictions similar to an initial model,
        to try to address the "catastrophic forgetting" problem. This feature is
        experimental.

        examples (Iterable[Example]): A batch of Example objects.
        drop (float): The dropout rate.
        sgd (thinc.api.Optimizer): The optimizer.
        losses (Dict[str, float]): Optional record of the loss during training.
            Updated using the component name as the key.
        RETURNS (Dict[str, float]): The updated losses dictionary.

        DOCS: https://spacy.io/api/tagger#rehearse
        """
        try:
            docs = [eg.predicted for eg in examples]
        except AttributeError:
            types = set([type(eg) for eg in examples])
            raise TypeError(Errors.E978.format(name="Tagger", method="rehearse", types=types)) from None
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
        """Find the loss and gradient of loss for the batch of documents and
        their predicted scores.

        examples (Iterable[Examples]): The batch of examples.
        scores: Scores representing the model's predictions.
        RETUTNRS (Tuple[float, float]): The loss and the gradient.

        DOCS: https://spacy.io/api/tagger#get_loss
        """
        loss_func = SequenceCategoricalCrossentropy(names=self.labels, normalize=False)
        truths = [eg.get_aligned("TAG", as_string=True) for eg in examples]
        d_scores, loss = loss_func(scores, truths)
        if self.model.ops.xp.isnan(loss):
            raise ValueError("nan value when computing loss")
        return float(loss), d_scores

    def begin_training(self, get_examples=lambda: [], *, pipeline=None, sgd=None):
        """Initialize the pipe for training, using data examples if available.

        get_examples (Callable[[], Iterable[Example]]): Optional function that
            returns gold-standard Example objects.
        pipeline (List[Tuple[str, Callable]]): Optional list of pipeline
            components that this component is part of. Corresponds to
            nlp.pipeline.
        sgd (thinc.api.Optimizer): Optional optimizer. Will be created with
            create_optimizer if it doesn't exist.
        RETURNS (thinc.api.Optimizer): The optimizer.

        DOCS: https://spacy.io/api/tagger#begin_training
        """
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
                raise TypeError(Errors.E978.format(name="Tagger", method="begin_training", types=type(example))) from None
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
        if sgd is None:
            sgd = self.create_optimizer()
        return sgd

    def add_label(self, label, values=None):
        """Add a new label to the pipe.

        label (str): The label to add.
        values (Dict[int, str]): Optional values to map to the label, e.g. a
            tag map dictionary.
        RETURNS (int): 0 if label is already present, otherwise 1.

        DOCS: https://spacy.io/api/tagger#add_label
        """
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

    def score(self, examples, **kwargs):
        """Score a batch of examples.

        examples (Iterable[Example]): The examples to score.
        RETURNS (Dict[str, Any]): The scores, produced by
            Scorer.score_token_attr for the attributes "tag", "pos" and "lemma".

        DOCS: https://spacy.io/api/tagger#score
        """
        scores = {}
        scores.update(Scorer.score_token_attr(examples, "tag", **kwargs))
        scores.update(Scorer.score_token_attr(examples, "pos", **kwargs))
        scores.update(Scorer.score_token_attr(examples, "lemma", **kwargs))
        return scores

    def to_bytes(self, *, exclude=tuple()):
        """Serialize the pipe to a bytestring.

        exclude (Iterable[str]): String names of serialization fields to exclude.
        RETURNS (bytes): The serialized object.

        DOCS: https://spacy.io/api/tagger#to_bytes
        """
        serialize = {}
        serialize["model"] = self.model.to_bytes
        serialize["vocab"] = self.vocab.to_bytes
        serialize["cfg"] = lambda: srsly.json_dumps(self.cfg)
        tag_map = dict(sorted(self.vocab.morphology.tag_map.items()))
        serialize["tag_map"] = lambda: srsly.msgpack_dumps(tag_map)
        morph_rules = dict(self.vocab.morphology.exc)
        serialize["morph_rules"] = lambda: srsly.msgpack_dumps(morph_rules)
        return util.to_bytes(serialize, exclude)

    def from_bytes(self, bytes_data, *, exclude=tuple()):
        """Load the pipe from a bytestring.

        bytes_data (bytes): The serialized pipe.
        exclude (Iterable[str]): String names of serialization fields to exclude.
        RETURNS (Tagger): The loaded Tagger.

        DOCS: https://spacy.io/api/tagger#from_bytes
        """
        def load_model(b):
            try:
                self.model.from_bytes(b)
            except AttributeError:
                raise ValueError(Errors.E149) from None

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

    def to_disk(self, path, *, exclude=tuple()):
        """Serialize the pipe to disk.

        path (str / Path): Path to a directory.
        exclude (Iterable[str]): String names of serialization fields to exclude.

        DOCS: https://spacy.io/api/tagger#to_disk
        """
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

    def from_disk(self, path, *, exclude=tuple()):
        """Load the pipe from disk. Modifies the object in place and returns it.

        path (str / Path): Path to a directory.
        exclude (Iterable[str]): String names of serialization fields to exclude.
        RETURNS (Tagger): The modified Tagger object.

        DOCS: https://spacy.io/api/tagger#from_disk
        """
        def load_model(p):
            with p.open("rb") as file_:
                try:
                    self.model.from_bytes(file_.read())
                except AttributeError:
                    raise ValueError(Errors.E149) from None

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

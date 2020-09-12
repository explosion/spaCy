from itertools import islice
from typing import Optional, Iterable, Callable, Dict, Iterator, Union, List, Tuple
from pathlib import Path
import srsly
import random
from thinc.api import CosineDistance, Model, Optimizer, Config
from thinc.api import set_dropout_rate
import warnings

from ..kb import KnowledgeBase, Candidate
from ..tokens import Doc
from .pipe import Pipe, deserialize_config
from ..language import Language
from ..vocab import Vocab
from ..training import Example, validate_examples
from ..errors import Errors, Warnings
from ..util import SimpleFrozenList
from .. import util


default_model_config = """
[model]
@architectures = "spacy.EntityLinker.v1"

[model.tok2vec]
@architectures = "spacy.HashEmbedCNN.v1"
pretrained_vectors = null
width = 96
depth = 2
embed_size = 300
window_size = 1
maxout_pieces = 3
subword_features = true
"""
DEFAULT_NEL_MODEL = Config().from_str(default_model_config)["model"]


@Language.factory(
    "entity_linker",
    requires=["doc.ents", "doc.sents", "token.ent_iob", "token.ent_type"],
    assigns=["token.ent_kb_id"],
    default_config={
        "kb_loader": {"@misc": "spacy.EmptyKB.v1", "entity_vector_length": 64},
        "model": DEFAULT_NEL_MODEL,
        "labels_discard": [],
        "incl_prior": True,
        "incl_context": True,
        "get_candidates": {"@misc": "spacy.CandidateGenerator.v1"},
    },
)
def make_entity_linker(
    nlp: Language,
    name: str,
    model: Model,
    kb_loader: Callable[[Vocab], KnowledgeBase],
    *,
    labels_discard: Iterable[str],
    incl_prior: bool,
    incl_context: bool,
    get_candidates: Callable[[KnowledgeBase, "Span"], Iterable[Candidate]],
):
    """Construct an EntityLinker component.

    model (Model[List[Doc], Floats2d]): A model that learns document vector
        representations. Given a batch of Doc objects, it should return a single
        array, with one row per item in the batch.
    kb (KnowledgeBase): The knowledge-base to link entities to.
    labels_discard (Iterable[str]): NER labels that will automatically get a "NIL" prediction.
    incl_prior (bool): Whether or not to include prior probabilities from the KB in the model.
    incl_context (bool): Whether or not to include the local context in the model.
    """
    return EntityLinker(
        nlp.vocab,
        model,
        name,
        kb_loader=kb_loader,
        labels_discard=labels_discard,
        incl_prior=incl_prior,
        incl_context=incl_context,
        get_candidates=get_candidates,
    )


class EntityLinker(Pipe):
    """Pipeline component for named entity linking.

    DOCS: https://nightly.spacy.io/api/entitylinker
    """

    NIL = "NIL"  # string used to refer to a non-existing link

    def __init__(
        self,
        vocab: Vocab,
        model: Model,
        name: str = "entity_linker",
        *,
        kb_loader: Callable[[Vocab], KnowledgeBase],
        labels_discard: Iterable[str],
        incl_prior: bool,
        incl_context: bool,
        get_candidates: Callable[[KnowledgeBase, "Span"], Iterable[Candidate]],
    ) -> None:
        """Initialize an entity linker.

        vocab (Vocab): The shared vocabulary.
        model (thinc.api.Model): The Thinc Model powering the pipeline component.
        name (str): The component instance name, used to add entries to the
            losses during training.
        kb_loader (Callable[[Vocab], KnowledgeBase]): A function that creates a KnowledgeBase from a Vocab instance.
        labels_discard (Iterable[str]): NER labels that will automatically get a "NIL" prediction.
        incl_prior (bool): Whether or not to include prior probabilities from the KB in the model.
        incl_context (bool): Whether or not to include the local context in the model.

        DOCS: https://nightly.spacy.io/api/entitylinker#init
        """
        self.vocab = vocab
        self.model = model
        self.name = name
        cfg = {
            "labels_discard": list(labels_discard),
            "incl_prior": incl_prior,
            "incl_context": incl_context,
        }
        self.kb = kb_loader(self.vocab)
        self.get_candidates = get_candidates
        self.cfg = dict(cfg)
        self.distance = CosineDistance(normalize=False)
        # how many neightbour sentences to take into account
        self.n_sents = cfg.get("n_sents", 0)

    def _require_kb(self) -> None:
        # Raise an error if the knowledge base is not initialized.
        if len(self.kb) == 0:
            raise ValueError(Errors.E139.format(name=self.name))

    def begin_training(
        self,
        get_examples: Callable[[], Iterable[Example]],
        *,
        pipeline: Optional[List[Tuple[str, Callable[[Doc], Doc]]]] = None,
        sgd: Optional[Optimizer] = None,
    ) -> Optimizer:
        """Initialize the pipe for training, using a representative set
        of data examples.

        get_examples (Callable[[], Iterable[Example]]): Function that
            returns a representative sample of gold-standard Example objects.
        pipeline (List[Tuple[str, Callable]]): Optional list of pipeline
            components that this component is part of. Corresponds to
            nlp.pipeline.
        sgd (thinc.api.Optimizer): Optional optimizer. Will be created with
            create_optimizer if it doesn't exist.
        RETURNS (thinc.api.Optimizer): The optimizer.

        DOCS: https://nightly.spacy.io/api/entitylinker#begin_training
        """
        self._ensure_examples(get_examples)
        self._require_kb()
        nO = self.kb.entity_vector_length
        doc_sample = []
        vector_sample = []
        for example in islice(get_examples(), 10):
            doc_sample.append(example.x)
            vector_sample.append(self.model.ops.alloc1f(nO))
        assert len(doc_sample) > 0, Errors.E923.format(name=self.name)
        assert len(vector_sample) > 0, Errors.E923.format(name=self.name)
        self.model.initialize(
            X=doc_sample, Y=self.model.ops.asarray(vector_sample, dtype="float32")
        )
        if sgd is None:
            sgd = self.create_optimizer()
        return sgd

    def update(
        self,
        examples: Iterable[Example],
        *,
        set_annotations: bool = False,
        drop: float = 0.0,
        sgd: Optional[Optimizer] = None,
        losses: Optional[Dict[str, float]] = None,
    ) -> Dict[str, float]:
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

        DOCS: https://nightly.spacy.io/api/entitylinker#update
        """
        self._require_kb()
        if losses is None:
            losses = {}
        losses.setdefault(self.name, 0.0)
        if not examples:
            return losses
        validate_examples(examples, "EntityLinker.update")
        sentence_docs = []
        docs = [eg.predicted for eg in examples]
        if set_annotations:
            # This seems simpler than other ways to get that exact output -- but
            # it does run the model twice :(
            predictions = self.model.predict(docs)
        for eg in examples:
            sentences = [s for s in eg.predicted.sents]
            kb_ids = eg.get_aligned("ENT_KB_ID", as_string=True)
            for ent in eg.predicted.ents:
                kb_id = kb_ids[
                    ent.start
                ]  # KB ID of the first token is the same as the whole span
                if kb_id:
                    try:
                        # find the sentence in the list of sentences.
                        sent_index = sentences.index(ent.sent)
                    except AttributeError:
                        # Catch the exception when ent.sent is None and provide a user-friendly warning
                        raise RuntimeError(Errors.E030) from None
                    # get n previous sentences, if there are any
                    start_sentence = max(0, sent_index - self.n_sents)
                    # get n posterior sentences, or as many < n as there are
                    end_sentence = min(len(sentences) - 1, sent_index + self.n_sents)
                    # get token positions
                    start_token = sentences[start_sentence].start
                    end_token = sentences[end_sentence].end
                    # append that span as a doc to training
                    sent_doc = eg.predicted[start_token:end_token].as_doc()
                    sentence_docs.append(sent_doc)
        set_dropout_rate(self.model, drop)
        if not sentence_docs:
            warnings.warn(Warnings.W093.format(name="Entity Linker"))
            return losses
        sentence_encodings, bp_context = self.model.begin_update(sentence_docs)
        loss, d_scores = self.get_loss(
            sentence_encodings=sentence_encodings, examples=examples
        )
        bp_context(d_scores)
        if sgd is not None:
            self.model.finish_update(sgd)
        losses[self.name] += loss
        if set_annotations:
            self.set_annotations(docs, predictions)
        return losses

    def get_loss(self, examples: Iterable[Example], sentence_encodings):
        validate_examples(examples, "EntityLinker.get_loss")
        entity_encodings = []
        for eg in examples:
            kb_ids = eg.get_aligned("ENT_KB_ID", as_string=True)
            for ent in eg.predicted.ents:
                kb_id = kb_ids[ent.start]
                if kb_id:
                    entity_encoding = self.kb.get_vector(kb_id)
                    entity_encodings.append(entity_encoding)
        entity_encodings = self.model.ops.asarray(entity_encodings, dtype="float32")
        if sentence_encodings.shape != entity_encodings.shape:
            err = Errors.E147.format(
                method="get_loss", msg="gold entities do not match up"
            )
            raise RuntimeError(err)
        gradients = self.distance.get_grad(sentence_encodings, entity_encodings)
        loss = self.distance.get_loss(sentence_encodings, entity_encodings)
        loss = loss / len(entity_encodings)
        return loss, gradients

    def __call__(self, doc: Doc) -> Doc:
        """Apply the pipe to a Doc.

        doc (Doc): The document to process.
        RETURNS (Doc): The processed Doc.

        DOCS: https://nightly.spacy.io/api/entitylinker#call
        """
        kb_ids = self.predict([doc])
        self.set_annotations([doc], kb_ids)
        return doc

    def pipe(self, stream: Iterable[Doc], *, batch_size: int = 128) -> Iterator[Doc]:
        """Apply the pipe to a stream of documents. This usually happens under
        the hood when the nlp object is called on a text and all components are
        applied to the Doc.

        stream (Iterable[Doc]): A stream of documents.
        batch_size (int): The number of documents to buffer.
        YIELDS (Doc): Processed documents in order.

        DOCS: https://nightly.spacy.io/api/entitylinker#pipe
        """
        for docs in util.minibatch(stream, size=batch_size):
            kb_ids = self.predict(docs)
            self.set_annotations(docs, kb_ids)
            yield from docs

    def predict(self, docs: Iterable[Doc]) -> List[str]:
        """Apply the pipeline's model to a batch of docs, without modifying them.
        Returns the KB IDs for each entity in each doc, including NIL if there is
        no prediction.

        docs (Iterable[Doc]): The documents to predict.
        RETURNS (List[int]): The models prediction for each document.

        DOCS: https://nightly.spacy.io/api/entitylinker#predict
        """
        self._require_kb()
        entity_count = 0
        final_kb_ids = []
        if not docs:
            return final_kb_ids
        if isinstance(docs, Doc):
            docs = [docs]
        for i, doc in enumerate(docs):
            sentences = [s for s in doc.sents]
            if len(doc) > 0:
                # Looping through each sentence and each entity
                # This may go wrong if there are entities across sentences - which shouldn't happen normally.
                for sent_index, sent in enumerate(sentences):
                    if sent.ents:
                        # get n_neightbour sentences, clipped to the length of the document
                        start_sentence = max(0, sent_index - self.n_sents)
                        end_sentence = min(
                            len(sentences) - 1, sent_index + self.n_sents
                        )
                        start_token = sentences[start_sentence].start
                        end_token = sentences[end_sentence].end
                        sent_doc = doc[start_token:end_token].as_doc()
                        # currently, the context is the same for each entity in a sentence (should be refined)
                        xp = self.model.ops.xp
                        if self.cfg.get("incl_context"):
                            sentence_encoding = self.model.predict([sent_doc])[0]
                            sentence_encoding_t = sentence_encoding.T
                            sentence_norm = xp.linalg.norm(sentence_encoding_t)
                        for ent in sent.ents:
                            entity_count += 1
                            to_discard = self.cfg.get("labels_discard", [])
                            if to_discard and ent.label_ in to_discard:
                                # ignoring this entity - setting to NIL
                                final_kb_ids.append(self.NIL)
                            else:
                                candidates = self.get_candidates(self.kb, ent)
                                if not candidates:
                                    # no prediction possible for this entity - setting to NIL
                                    final_kb_ids.append(self.NIL)
                                elif len(candidates) == 1:
                                    # shortcut for efficiency reasons: take the 1 candidate
                                    # TODO: thresholding
                                    final_kb_ids.append(candidates[0].entity_)
                                else:
                                    random.shuffle(candidates)
                                    # set all prior probabilities to 0 if incl_prior=False
                                    prior_probs = xp.asarray(
                                        [c.prior_prob for c in candidates]
                                    )
                                    if not self.cfg.get("incl_prior"):
                                        prior_probs = xp.asarray(
                                            [0.0 for _ in candidates]
                                        )
                                    scores = prior_probs
                                    # add in similarity from the context
                                    if self.cfg.get("incl_context"):
                                        entity_encodings = xp.asarray(
                                            [c.entity_vector for c in candidates]
                                        )
                                        entity_norm = xp.linalg.norm(
                                            entity_encodings, axis=1
                                        )
                                        if len(entity_encodings) != len(prior_probs):
                                            raise RuntimeError(
                                                Errors.E147.format(
                                                    method="predict",
                                                    msg="vectors not of equal length",
                                                )
                                            )
                                        # cosine similarity
                                        sims = xp.dot(
                                            entity_encodings, sentence_encoding_t
                                        ) / (sentence_norm * entity_norm)
                                        if sims.shape != prior_probs.shape:
                                            raise ValueError(Errors.E161)
                                        scores = (
                                            prior_probs + sims - (prior_probs * sims)
                                        )
                                    # TODO: thresholding
                                    best_index = scores.argmax().item()
                                    best_candidate = candidates[best_index]
                                    final_kb_ids.append(best_candidate.entity_)
        if not (len(final_kb_ids) == entity_count):
            err = Errors.E147.format(
                method="predict", msg="result variables not of equal length"
            )
            raise RuntimeError(err)
        return final_kb_ids

    def set_annotations(self, docs: Iterable[Doc], kb_ids: List[str]) -> None:
        """Modify a batch of documents, using pre-computed scores.

        docs (Iterable[Doc]): The documents to modify.
        kb_ids (List[str]): The IDs to set, produced by EntityLinker.predict.

        DOCS: https://nightly.spacy.io/api/entitylinker#set_annotations
        """
        count_ents = len([ent for doc in docs for ent in doc.ents])
        if count_ents != len(kb_ids):
            raise ValueError(Errors.E148.format(ents=count_ents, ids=len(kb_ids)))
        i = 0
        for doc in docs:
            for ent in doc.ents:
                kb_id = kb_ids[i]
                i += 1
                for token in ent:
                    token.ent_kb_id_ = kb_id

    def to_disk(
        self, path: Union[str, Path], *, exclude: Iterable[str] = SimpleFrozenList()
    ) -> None:
        """Serialize the pipe to disk.

        path (str / Path): Path to a directory.
        exclude (Iterable[str]): String names of serialization fields to exclude.

        DOCS: https://nightly.spacy.io/api/entitylinker#to_disk
        """
        serialize = {}
        serialize["cfg"] = lambda p: srsly.write_json(p, self.cfg)
        serialize["vocab"] = lambda p: self.vocab.to_disk(p)
        serialize["kb"] = lambda p: self.kb.to_disk(p)
        serialize["model"] = lambda p: self.model.to_disk(p)
        util.to_disk(path, serialize, exclude)

    def from_disk(
        self, path: Union[str, Path], *, exclude: Iterable[str] = SimpleFrozenList()
    ) -> "EntityLinker":
        """Load the pipe from disk. Modifies the object in place and returns it.

        path (str / Path): Path to a directory.
        exclude (Iterable[str]): String names of serialization fields to exclude.
        RETURNS (EntityLinker): The modified EntityLinker object.

        DOCS: https://nightly.spacy.io/api/entitylinker#from_disk
        """

        def load_model(p):
            try:
                self.model.from_bytes(p.open("rb").read())
            except AttributeError:
                raise ValueError(Errors.E149) from None

        deserialize = {}
        deserialize["vocab"] = lambda p: self.vocab.from_disk(p)
        deserialize["cfg"] = lambda p: self.cfg.update(deserialize_config(p))
        deserialize["kb"] = lambda p: self.kb.from_disk(p)
        deserialize["model"] = load_model
        util.from_disk(path, deserialize, exclude)
        return self

    def rehearse(self, examples, *, sgd=None, losses=None, **config):
        raise NotImplementedError

    def add_label(self, label):
        raise NotImplementedError

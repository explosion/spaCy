# This file is present to provide a prior version of the EntityLinker component
# for backwards compatibility. For details see #9669.

import random
import warnings
from itertools import islice
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Union

import srsly
from thinc.api import CosineDistance, Model, Optimizer, set_dropout_rate
from thinc.types import Floats2d

from ... import util
from ...errors import Errors, Warnings
from ...kb import Candidate, KnowledgeBase
from ...language import Language
from ...ml import empty_kb
from ...scorer import Scorer
from ...tokens import Doc, Span
from ...training import Example, validate_examples, validate_get_examples
from ...util import SimpleFrozenList
from ...vocab import Vocab
from ..pipe import deserialize_config
from ..trainable_pipe import TrainablePipe

# See #9050
BACKWARD_OVERWRITE = True


def entity_linker_score(examples, **kwargs):
    return Scorer.score_links(examples, negative_labels=[EntityLinker_v1.NIL], **kwargs)


class EntityLinker_v1(TrainablePipe):
    """Pipeline component for named entity linking.

    DOCS: https://spacy.io/api/entitylinker
    """

    NIL = "NIL"  # string used to refer to a non-existing link

    def __init__(
        self,
        vocab: Vocab,
        model: Model,
        name: str = "entity_linker",
        *,
        labels_discard: Iterable[str],
        n_sents: int,
        incl_prior: bool,
        incl_context: bool,
        entity_vector_length: int,
        get_candidates: Callable[[KnowledgeBase, Span], Iterable[Candidate]],
        overwrite: bool = BACKWARD_OVERWRITE,
        scorer: Optional[Callable] = entity_linker_score,
    ) -> None:
        """Initialize an entity linker.

        vocab (Vocab): The shared vocabulary.
        model (thinc.api.Model): The Thinc Model powering the pipeline component.
        name (str): The component instance name, used to add entries to the
            losses during training.
        labels_discard (Iterable[str]): NER labels that will automatically get a "NIL" prediction.
        n_sents (int): The number of neighbouring sentences to take into account.
        incl_prior (bool): Whether or not to include prior probabilities from the KB in the model.
        incl_context (bool): Whether or not to include the local context in the model.
        entity_vector_length (int): Size of encoding vectors in the KB.
        get_candidates (Callable[[KnowledgeBase, Span], Iterable[Candidate]]): Function that
            produces a list of candidates, given a certain knowledge base and a textual mention.
        scorer (Optional[Callable]): The scoring method. Defaults to Scorer.score_links.
        DOCS: https://spacy.io/api/entitylinker#init
        """
        self.vocab = vocab
        self.model = model
        self.name = name
        self.labels_discard = list(labels_discard)
        self.n_sents = n_sents
        self.incl_prior = incl_prior
        self.incl_context = incl_context
        self.get_candidates = get_candidates
        self.cfg: Dict[str, Any] = {"overwrite": overwrite}
        self.distance = CosineDistance(normalize=False)
        # how many neighbour sentences to take into account
        # create an empty KB by default. If you want to load a predefined one, specify it in 'initialize'.
        self.kb = empty_kb(entity_vector_length)(self.vocab)
        self.scorer = scorer

    def set_kb(self, kb_loader: Callable[[Vocab], KnowledgeBase]):
        """Define the KB of this pipe by providing a function that will
        create it using this object's vocab."""
        if not callable(kb_loader):
            raise ValueError(Errors.E885.format(arg_type=type(kb_loader)))

        self.kb = kb_loader(self.vocab)

    def validate_kb(self) -> None:
        # Raise an error if the knowledge base is not initialized.
        if self.kb is None:
            raise ValueError(Errors.E1018.format(name=self.name))
        if len(self.kb) == 0:
            raise ValueError(Errors.E139.format(name=self.name))

    def initialize(
        self,
        get_examples: Callable[[], Iterable[Example]],
        *,
        nlp: Optional[Language] = None,
        kb_loader: Optional[Callable[[Vocab], KnowledgeBase]] = None,
    ):
        """Initialize the pipe for training, using a representative set
        of data examples.

        get_examples (Callable[[], Iterable[Example]]): Function that
            returns a representative sample of gold-standard Example objects.
        nlp (Language): The current nlp object the component is part of.
        kb_loader (Callable[[Vocab], KnowledgeBase]): A function that creates an InMemoryLookupKB from a Vocab instance.
            Note that providing this argument, will overwrite all data accumulated in the current KB.
            Use this only when loading a KB as-such from file.

        DOCS: https://spacy.io/api/entitylinker#initialize
        """
        validate_get_examples(get_examples, "EntityLinker_v1.initialize")
        if kb_loader is not None:
            self.set_kb(kb_loader)
        self.validate_kb()
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

    def update(
        self,
        examples: Iterable[Example],
        *,
        drop: float = 0.0,
        sgd: Optional[Optimizer] = None,
        losses: Optional[Dict[str, float]] = None,
    ) -> Dict[str, float]:
        """Learn from a batch of documents and gold-standard information,
        updating the pipe's model. Delegates to predict and get_loss.

        examples (Iterable[Example]): A batch of Example objects.
        drop (float): The dropout rate.
        sgd (thinc.api.Optimizer): The optimizer.
        losses (Dict[str, float]): Optional record of the loss during training.
            Updated using the component name as the key.
        RETURNS (Dict[str, float]): The updated losses dictionary.

        DOCS: https://spacy.io/api/entitylinker#update
        """
        self.validate_kb()
        if losses is None:
            losses = {}
        losses.setdefault(self.name, 0.0)
        if not examples:
            return losses
        validate_examples(examples, "EntityLinker_v1.update")
        sentence_docs = []
        for eg in examples:
            sentences = [s for s in eg.reference.sents]
            kb_ids = eg.get_aligned("ENT_KB_ID", as_string=True)
            for ent in eg.reference.ents:
                # KB ID of the first token is the same as the whole span
                kb_id = kb_ids[ent.start]
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
            self.finish_update(sgd)
        losses[self.name] += loss
        return losses

    def get_loss(self, examples: Iterable[Example], sentence_encodings: Floats2d):
        validate_examples(examples, "EntityLinker_v1.get_loss")
        entity_encodings = []
        for eg in examples:
            kb_ids = eg.get_aligned("ENT_KB_ID", as_string=True)
            for ent in eg.reference.ents:
                kb_id = kb_ids[ent.start]
                if kb_id:
                    entity_encoding = self.kb.get_vector(kb_id)
                    entity_encodings.append(entity_encoding)
        entity_encodings = self.model.ops.asarray2f(entity_encodings)
        if sentence_encodings.shape != entity_encodings.shape:
            err = Errors.E147.format(
                method="get_loss", msg="gold entities do not match up"
            )
            raise RuntimeError(err)
        gradients = self.distance.get_grad(sentence_encodings, entity_encodings)
        loss = self.distance.get_loss(sentence_encodings, entity_encodings)
        loss = loss / len(entity_encodings)
        return float(loss), gradients

    def predict(self, docs: Iterable[Doc]) -> List[str]:
        """Apply the pipeline's model to a batch of docs, without modifying them.
        Returns the KB IDs for each entity in each doc, including NIL if there is
        no prediction.

        docs (Iterable[Doc]): The documents to predict.
        RETURNS (List[str]): The models prediction for each document.

        DOCS: https://spacy.io/api/entitylinker#predict
        """
        self.validate_kb()
        entity_count = 0
        final_kb_ids: List[str] = []
        if not docs:
            return final_kb_ids
        if isinstance(docs, Doc):
            docs = [docs]
        for i, doc in enumerate(docs):
            sentences = [s for s in doc.sents]
            if len(doc) > 0:
                # Looping through each entity (TODO: rewrite)
                for ent in doc.ents:
                    sent = ent.sent
                    sent_index = sentences.index(sent)
                    assert sent_index >= 0
                    # get n_neighbour sentences, clipped to the length of the document
                    start_sentence = max(0, sent_index - self.n_sents)
                    end_sentence = min(len(sentences) - 1, sent_index + self.n_sents)
                    start_token = sentences[start_sentence].start
                    end_token = sentences[end_sentence].end
                    sent_doc = doc[start_token:end_token].as_doc()
                    # currently, the context is the same for each entity in a sentence (should be refined)
                    xp = self.model.ops.xp
                    if self.incl_context:
                        sentence_encoding = self.model.predict([sent_doc])[0]
                        sentence_encoding_t = sentence_encoding.T
                        sentence_norm = xp.linalg.norm(sentence_encoding_t)
                    entity_count += 1
                    if ent.label_ in self.labels_discard:
                        # ignoring this entity - setting to NIL
                        final_kb_ids.append(self.NIL)
                    else:
                        candidates = list(self.get_candidates(self.kb, ent))
                        if not candidates:
                            # no prediction possible for this entity - setting to NIL
                            final_kb_ids.append(self.NIL)
                        elif len(candidates) == 1:
                            # shortcut for efficiency reasons: take the 1 candidate
                            final_kb_ids.append(candidates[0].entity_)
                        else:
                            random.shuffle(candidates)
                            # set all prior probabilities to 0 if incl_prior=False
                            prior_probs = xp.asarray([c.prior_prob for c in candidates])
                            if not self.incl_prior:
                                prior_probs = xp.asarray([0.0 for _ in candidates])
                            scores = prior_probs
                            # add in similarity from the context
                            if self.incl_context:
                                entity_encodings = xp.asarray(
                                    [c.entity_vector for c in candidates]
                                )
                                entity_norm = xp.linalg.norm(entity_encodings, axis=1)
                                if len(entity_encodings) != len(prior_probs):
                                    raise RuntimeError(
                                        Errors.E147.format(
                                            method="predict",
                                            msg="vectors not of equal length",
                                        )
                                    )
                                # cosine similarity
                                sims = xp.dot(entity_encodings, sentence_encoding_t) / (
                                    sentence_norm * entity_norm
                                )
                                if sims.shape != prior_probs.shape:
                                    raise ValueError(Errors.E161)
                                scores = prior_probs + sims - (prior_probs * sims)
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

        DOCS: https://spacy.io/api/entitylinker#set_annotations
        """
        count_ents = len([ent for doc in docs for ent in doc.ents])
        if count_ents != len(kb_ids):
            raise ValueError(Errors.E148.format(ents=count_ents, ids=len(kb_ids)))
        i = 0
        overwrite = self.cfg["overwrite"]
        for doc in docs:
            for ent in doc.ents:
                kb_id = kb_ids[i]
                i += 1
                for token in ent:
                    if token.ent_kb_id == 0 or overwrite:
                        token.ent_kb_id_ = kb_id

    def to_bytes(self, *, exclude=tuple()):
        """Serialize the pipe to a bytestring.

        exclude (Iterable[str]): String names of serialization fields to exclude.
        RETURNS (bytes): The serialized object.

        DOCS: https://spacy.io/api/entitylinker#to_bytes
        """
        self._validate_serialization_attrs()
        serialize = {}
        if hasattr(self, "cfg") and self.cfg is not None:
            serialize["cfg"] = lambda: srsly.json_dumps(self.cfg)
        serialize["vocab"] = lambda: self.vocab.to_bytes(exclude=exclude)
        serialize["kb"] = self.kb.to_bytes
        serialize["model"] = self.model.to_bytes
        return util.to_bytes(serialize, exclude)

    def from_bytes(self, bytes_data, *, exclude=tuple()):
        """Load the pipe from a bytestring.

        exclude (Iterable[str]): String names of serialization fields to exclude.
        RETURNS (TrainablePipe): The loaded object.

        DOCS: https://spacy.io/api/entitylinker#from_bytes
        """
        self._validate_serialization_attrs()

        def load_model(b):
            try:
                self.model.from_bytes(b)
            except AttributeError:
                raise ValueError(Errors.E149) from None

        deserialize = {}
        if hasattr(self, "cfg") and self.cfg is not None:
            deserialize["cfg"] = lambda b: self.cfg.update(srsly.json_loads(b))
        deserialize["vocab"] = lambda b: self.vocab.from_bytes(b, exclude=exclude)
        deserialize["kb"] = lambda b: self.kb.from_bytes(b)
        deserialize["model"] = load_model
        util.from_bytes(bytes_data, deserialize, exclude)
        return self

    def to_disk(
        self, path: Union[str, Path], *, exclude: Iterable[str] = SimpleFrozenList()
    ) -> None:
        """Serialize the pipe to disk.

        path (str / Path): Path to a directory.
        exclude (Iterable[str]): String names of serialization fields to exclude.

        DOCS: https://spacy.io/api/entitylinker#to_disk
        """
        serialize = {}
        serialize["vocab"] = lambda p: self.vocab.to_disk(p, exclude=exclude)
        serialize["cfg"] = lambda p: srsly.write_json(p, self.cfg)
        serialize["kb"] = lambda p: self.kb.to_disk(p)
        serialize["model"] = lambda p: self.model.to_disk(p)
        util.to_disk(path, serialize, exclude)

    def from_disk(
        self, path: Union[str, Path], *, exclude: Iterable[str] = SimpleFrozenList()
    ) -> "EntityLinker_v1":
        """Load the pipe from disk. Modifies the object in place and returns it.

        path (str / Path): Path to a directory.
        exclude (Iterable[str]): String names of serialization fields to exclude.
        RETURNS (EntityLinker): The modified EntityLinker object.

        DOCS: https://spacy.io/api/entitylinker#from_disk
        """

        def load_model(p):
            try:
                with p.open("rb") as infile:
                    self.model.from_bytes(infile.read())
            except AttributeError:
                raise ValueError(Errors.E149) from None

        deserialize: Dict[str, Callable[[Any], Any]] = {}
        deserialize["cfg"] = lambda p: self.cfg.update(deserialize_config(p))
        deserialize["vocab"] = lambda p: self.vocab.from_disk(p, exclude=exclude)
        deserialize["kb"] = lambda p: self.kb.from_disk(p)
        deserialize["model"] = load_model
        util.from_disk(path, deserialize, exclude)
        return self

    def rehearse(self, examples, *, sgd=None, losses=None, **config):
        raise NotImplementedError

    def add_label(self, label):
        raise NotImplementedError

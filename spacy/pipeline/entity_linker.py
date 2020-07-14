import srsly
import random
from typing import Optional, Iterable

from thinc.api import CosineDistance, get_array_module, Model
from thinc.api import set_dropout_rate, SequenceCategoricalCrossentropy
import warnings

from ..kb import KnowledgeBase
from ..tokens import Doc
from .pipes import Pipe, _load_cfg
from ..language import Language
from ..errors import Errors, Warnings
from .. import util
from ..util import load_config_from_str


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
dropout = null
"""
DEFAULT_NEL_MODEL = load_config_from_str(default_model_config, create_objects=False)["model"]


@Language.factory(
    "entity_linker",
    requires=["doc.ents", "doc.sents", "token.ent_iob", "token.ent_type"],
    assigns=["token.ent_kb_id"],
    default_config={
        "kb": None,  # TODO - what kind of default makes sense here?
        "labels_discard": [],
        "incl_prior": True,
        "incl_context": True,
        "model": DEFAULT_NEL_MODEL,
    },
)
def make_entity_linker(
    nlp: Language,
    name: str,
    model: Model,
    kb: Optional[KnowledgeBase],
    labels_discard: Iterable[str],
    incl_prior: bool,
    incl_context: bool,
):
    return EntityLinker(
        nlp.vocab,
        model,
        name,
        kb=kb,
        labels_discard=labels_discard,
        incl_prior=incl_prior,
        incl_context=incl_context,
    )


class EntityLinker(Pipe):
    """Pipeline component for named entity linking.

    DOCS: https://spacy.io/api/entitylinker
    """

    NIL = "NIL"  # string used to refer to a non-existing link

    def __init__(
        self,
        vocab,
        model,
        name="entity_linker",
        kb=None,
        labels_discard=tuple(),
        incl_prior=True,
        incl_context=True,
    ):
        self.vocab = vocab
        self.model = model
        self.name = name
        cfg = {
            "kb": kb,
            "labels_discard": list(labels_discard),
            "incl_prior": incl_prior,
            "incl_context": incl_context,
        }
        self.kb = kb
        if self.kb is None:
            # create an empty KB that should be filled by calling from_disk
            self.kb = KnowledgeBase(vocab=vocab)
        else:
            del cfg["kb"]  # we don't want to duplicate its serialization
        if not isinstance(self.kb, KnowledgeBase):
            raise ValueError(Errors.E990.format(type=type(self.kb)))
        self.cfg = dict(cfg)
        self.distance = CosineDistance(normalize=False)
        # how many neightbour sentences to take into account
        self.n_sents = cfg.get("n_sents", 0)

    def require_kb(self):
        # Raise an error if the knowledge base is not initialized.
        if len(self.kb) == 0:
            raise ValueError(Errors.E139.format(name=self.name))

    def begin_training(
        self, get_examples=lambda: [], pipeline=None, sgd=None, **kwargs
    ):
        self.require_kb()
        nO = self.kb.entity_vector_length
        self.set_output(nO)
        self.model.initialize()
        if sgd is None:
            sgd = self.create_optimizer()
        return sgd

    def update(
        self, examples, *, set_annotations=False, drop=0.0, sgd=None, losses=None
    ):
        self.require_kb()
        if losses is None:
            losses = {}
        losses.setdefault(self.name, 0.0)
        if not examples:
            return losses
        sentence_docs = []
        try:
            docs = [eg.predicted for eg in examples]
        except AttributeError:
            types = set([type(eg) for eg in examples])
            raise TypeError(
                Errors.E978.format(name="EntityLinker", method="update", types=types)
            )
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
                        raise RuntimeError(Errors.E030)
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
            return 0.0
        sentence_encodings, bp_context = self.model.begin_update(sentence_docs)
        loss, d_scores = self.get_similarity_loss(
            sentence_encodings=sentence_encodings, examples=examples
        )
        bp_context(d_scores)
        if sgd is not None:
            self.model.finish_update(sgd)
        losses[self.name] += loss
        if set_annotations:
            self.set_annotations(docs, predictions)
        return losses

    def get_similarity_loss(self, examples, sentence_encodings):
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
            raise RuntimeError(
                Errors.E147.format(
                    method="get_similarity_loss", msg="gold entities do not match up"
                )
            )
        gradients = self.distance.get_grad(sentence_encodings, entity_encodings)
        loss = self.distance.get_loss(sentence_encodings, entity_encodings)
        loss = loss / len(entity_encodings)
        return loss, gradients

    def __call__(self, doc):
        kb_ids = self.predict([doc])
        self.set_annotations([doc], kb_ids)
        return doc

    def pipe(self, stream, batch_size=128):
        for docs in util.minibatch(stream, size=batch_size):
            kb_ids = self.predict(docs)
            self.set_annotations(docs, kb_ids)
            yield from docs

    def predict(self, docs):
        """ Return the KB IDs for each entity in each doc, including NIL if there is no prediction """
        self.require_kb()
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
                        sentence_encoding = self.model.predict([sent_doc])[0]
                        xp = get_array_module(sentence_encoding)
                        sentence_encoding_t = sentence_encoding.T
                        sentence_norm = xp.linalg.norm(sentence_encoding_t)
                        for ent in sent.ents:
                            entity_count += 1
                            to_discard = self.cfg.get("labels_discard", [])
                            if to_discard and ent.label_ in to_discard:
                                # ignoring this entity - setting to NIL
                                final_kb_ids.append(self.NIL)
                            else:
                                candidates = self.kb.get_candidates(ent.text)
                                if not candidates:
                                    # no prediction possible for this entity - setting to NIL
                                    final_kb_ids.append(self.NIL)
                                elif len(candidates) == 1:
                                    # shortcut for efficiency reasons: take the 1 candidate
                                    # TODO: thresholding
                                    final_kb_ids.append(candidates[0].entity_)
                                else:
                                    random.shuffle(candidates)
                                    # this will set all prior probabilities to 0 if they should be excluded from the model
                                    prior_probs = xp.asarray(
                                        [c.prior_prob for c in candidates]
                                    )
                                    if not self.cfg.get("incl_prior", True):
                                        prior_probs = xp.asarray(
                                            [0.0 for c in candidates]
                                        )
                                    scores = prior_probs
                                    # add in similarity from the context
                                    if self.cfg.get("incl_context", True):
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
            raise RuntimeError(
                Errors.E147.format(
                    method="predict", msg="result variables not of equal length"
                )
            )
        return final_kb_ids

    def set_annotations(self, docs, kb_ids):
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

    def to_disk(self, path, exclude=tuple()):
        serialize = {}
        self.cfg["entity_width"] = self.kb.entity_vector_length
        serialize["cfg"] = lambda p: srsly.write_json(p, self.cfg)
        serialize["vocab"] = lambda p: self.vocab.to_disk(p)
        serialize["kb"] = lambda p: self.kb.dump(p)
        serialize["model"] = lambda p: self.model.to_disk(p)
        util.to_disk(path, serialize, exclude)

    def from_disk(self, path, exclude=tuple()):
        def load_model(p):
            try:
                self.model.from_bytes(p.open("rb").read())
            except AttributeError:
                raise ValueError(Errors.E149)

        def load_kb(p):
            self.kb = KnowledgeBase(
                vocab=self.vocab, entity_vector_length=self.cfg["entity_width"]
            )
            self.kb.load_bulk(p)

        deserialize = {}
        deserialize["vocab"] = lambda p: self.vocab.from_disk(p)
        deserialize["cfg"] = lambda p: self.cfg.update(_load_cfg(p))
        deserialize["kb"] = load_kb
        deserialize["model"] = load_model
        util.from_disk(path, deserialize, exclude)
        return self

    def rehearse(self, examples, sgd=None, losses=None, **config):
        raise NotImplementedError

    def add_label(self, label):
        raise NotImplementedError

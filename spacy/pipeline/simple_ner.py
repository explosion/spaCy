from typing import List
from thinc.types import Floats2d
from thinc.api import CategoricalCrossentropy, set_dropout_rate
from ..gold import Example, spans_from_biluo_tags
from ..tokens import Doc
from ..language import component
from ..util import link_vectors_to_models
from .pipes import Pipe


@component("simple_ner", assigns=["doc.ents"])
class SimpleNER(Pipe):
    """Named entity recognition with a tagging model. The model should include
    validity constraints to ensure that only valid tag sequences are returned."""

    def __init__(self, vocab, model):
        self.vocab = vocab
        self.model = model
        self.cfg = {"labels": []}
        assert self.model is not None

    @property
    def labels(self):
        return self.cfg["labels"]

    def add_label(self, label):
        if label not in self.cfg["labels"]:
            self.cfg["labels"].append(label)
 
    def get_tag_names(self):
        return (
            [f"B-{label}" for label in self.labels] +
            [f"I-{label}" for label in self.labels] +
            [f"L-{label}" for label in self.labels] +
            [f"U-{label}" for label in self.labels] +
            ["O"]
        )

    def predict(self, docs: List[Doc]) -> List[Floats2d]:
        scores = self.model.predict(docs)
        return scores

    def set_annotations(self, docs: List[Doc], scores: List[Floats2d], tensors=None):
        """Set entities on a batch of documents from a batch of scores."""
        tag_names = self.get_tag_names()
        for i, doc in enumerate(docs):
            actions = scores[i].argmax(axis=1)
            tags = [tag_names[actions[j]] for j in range(len(doc))]
            doc.ents = spans_from_biluo_tags(doc, tags)

    def update(self, examples, set_annotations=False, drop=0.0, sgd=None, losses=None):
        tag_names = self.get_tag_names()
        examples = Example.to_example_objects(examples)
        examples = [eg for eg in examples if _has_ner(eg)]
        if not examples:
            return 0
        docs = [ex.doc for ex in examples]
        set_dropout_rate(self.model, drop)
        scores, bp_scores = self.model.begin_update(docs)
        loss, d_scores = self.get_loss(examples, scores)
        bp_scores(d_scores)
        if set_annotations:
            self.set_annotations(docs, scores)
        if sgd is not None:
            self.model.finish_update(sgd)
        if losses is not None:
            losses.setdefault("ner", 0.0)
            losses["ner"] += loss
        return loss

    def get_loss(self, examples, scores):
        loss_func = CategoricalCrossentropy(names=self.get_tag_names())
        loss = 0
        d_scores = []
        for eg, doc_scores in zip(examples, scores):
            d_doc_scores, doc_loss = loss_func(doc_scores, eg.gold.ner)
            d_scores.append(d_doc_scores)
            loss += doc_loss
        return loss, d_scores

    def begin_training(self, get_examples, pipeline=None, sgd=None, **kwargs):
        self.cfg.update(kwargs)
        if not hasattr(get_examples, '__call__'):
            gold_tuples = get_examples
            get_examples = lambda: gold_tuples
        labels = _get_labels(get_examples())
        for label in _get_labels(get_examples()):
            self.add_label(label)
        labels = self.labels
        n_actions = self.model.attrs["get_num_actions"](len(labels))
        self.model.set_dim("nO", n_actions)
        self.model.initialize() 
        if pipeline is not None:
            self.init_multitask_objectives(get_examples, pipeline, sgd=sgd, **self.cfg)
        link_vectors_to_models(self.vocab)
        return sgd

    def init_multitask_objectives(self, *args, **kwargs):
        pass


def _has_ner(eg):
    for ner_tag in eg.token_annotation.entities:
        if ner_tag != "-" and ner_tag != None:
            return True
    else:
        return False


def _get_labels(examples):
    labels = set()
    for eg in examples:
        for ner_tag in eg.token_annotation.entities:
            if ner_tag != 'O' and ner_tag != '-':
                _, label = ner_tag.split('-', 1)
                labels.add(label)
    return list(sorted(labels))

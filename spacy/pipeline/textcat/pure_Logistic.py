from typing import List, Dict, Iterable
import numpy as np
from spacy.pipeline import TrainablePipe
from spacy.language import Language
from spacy.training import Example
from spacy.vocab import Vocab
from spacy.tokens import Doc


@Language.factory(
    "pure_logistic_textcat",
    default_config={
        "learning_rate": 0.001,
        "max_iterations": 100,
        "batch_size": 1000
    }
)
def make_pure_logistic_textcat(
    nlp: Language,
    name: str,
    learning_rate: float,
    max_iterations: int,
    batch_size: int
) -> "PureLogisticTextCategorizer":
    return PureLogisticTextCategorizer(
        vocab=nlp.vocab,
        name=name,
        learning_rate=learning_rate,
        max_iterations=max_iterations,
        batch_size=batch_size
    )


class PureLogisticTextCategorizer(TrainablePipe):
    def __init__(
        self,
        vocab: Vocab,
        name: str = "pure_logistic_textcat",
        *,
        learning_rate: float = 0.001,
        max_iterations: int = 100,
        batch_size: int = 1000
    ):
        """Initialize the text categorizer."""
        self.vocab = vocab
        self.name = name
        self.learning_rate = learning_rate
        self.max_iterations = max_iterations
        self.batch_size = batch_size
        self.weights = None
        self.bias = 0.0
        self._labels = set()  # Use _labels as internal attribute

        # Register the custom extension attribute if it doesn't exist
        if not Doc.has_extension("textcat_scores"):
            Doc.set_extension("textcat_scores", default=None)

    @property
    def labels(self):
        """Get the labels."""
        return self._labels

    @labels.setter
    def labels(self, value):
        """Set the labels."""
        self._labels = value

    def predict(self, docs):
        """Apply the pipe to a batch of docs, returning scores."""
        scores = self._predict_scores(docs)
        for doc, doc_scores in zip(docs, scores):
            doc._.textcat_scores = doc_scores
        return docs

    def _predict_scores(self, docs):
        """Predict scores for docs."""
        features = self._extract_features(docs)
        scores = []
        for doc_features in features:
            if self.weights is None:
                doc_scores = {"positive": 0.5, "negative": 0.5}
            else:
                logits = np.dot(doc_features, self.weights) + self.bias
                prob = 1 / (1 + np.exp(-logits))
                doc_scores = {
                    "positive": float(prob),
                    "negative": float(1 - prob)
                }
            scores.append(doc_scores)
        return scores

    def set_annotations(self, docs, scores):
        """Set the predicted annotations (e.g. categories) on the docs."""
        for doc, score in zip(docs, scores):
            doc.cats = {label: score[i] for i, label in enumerate(self._labels)}

    def _extract_features(self, docs) -> List[np.ndarray]:
        """Extract features from docs."""
        features = []
        for doc in docs:
            # Basic features
            doc_vector = doc.vector
            n_tokens = len(doc)

            # Additional features
            n_entities = len(doc.ents)
            avg_token_length = np.mean([len(token.text) for token in doc])
            n_stopwords = len([token for token in doc if token.is_stop])

            # Combine features
            doc_features = np.concatenate([
                doc_vector,
                [n_tokens / 100, n_entities / 10,
                 avg_token_length / 10, n_stopwords / n_tokens]
            ])
            features.append(doc_features)
        return features

    def update(
        self,
        examples: Iterable[Example],
        *,
        drop: float = 0.0,
        sgd=None,
        losses: Dict[str, float] = None
    ) -> Dict[str, float]:
        """Update the model."""
        losses = {} if losses is None else losses

        # Update label set
        for example in examples:
            self._labels.update(example.reference.cats.keys())

        # Extract features and labels
        docs = [example.reference for example in examples]
        label_arrays = self._make_label_array([example.reference.cats for example in examples])

        features = self._extract_features(docs)

        if self.weights is None:
            n_features = features[0].shape[0] if features else 0
            self.weights = np.zeros((n_features, 1))

        # Simple gradient descent
        total_loss = 0.0
        for i in range(self.max_iterations):
            for feat, gold in zip(features, label_arrays):
                pred = 1 / (1 + np.exp(-(np.dot(feat, self.weights) + self.bias)))
                loss = -np.mean(gold * np.log(pred + 1e-8) +
                                (1 - gold) * np.log(1 - pred + 1e-8))
                total_loss += loss

                # Compute gradients
                d_weights = feat.reshape(-1, 1) * (pred - gold)
                d_bias = pred - gold

                # Update weights
                self.weights -= self.learning_rate * d_weights
                self.bias -= self.learning_rate * float(d_bias)

        losses[self.name] = total_loss / len(examples)
        return losses

    def _make_label_array(self, cats):
        """Convert label dicts into an array."""
        arr = np.zeros((len(cats),))
        for i, cat_dict in enumerate(cats):
            if cat_dict.get("positive", 0) > 0.5:
                arr[i] = 1.0
        return arr.reshape(-1, 1)

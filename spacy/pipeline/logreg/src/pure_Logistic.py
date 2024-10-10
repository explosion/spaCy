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
    """
    Factory function to create an instance of PureLogisticTextCategorizer.
    :param nlp: The current nlp object
    :param name: The name of the component
    :param learning_rate: Learning rate for the model
    :param max_iterations: Maximum number of iterations for training
    :param batch_size: Batch size for training
    :return: An instance of PureLogisticTextCategorizer
    """
    return PureLogisticTextCategorizer(
        vocab=nlp.vocab,
        name=name,
        learning_rate=learning_rate,
        max_iterations=max_iterations,
        batch_size=batch_size
    )


class PureLogisticTextCategorizer(TrainablePipe):
    """
    A custom text categorizer using logistic regression.
    """
    def __init__(
        self,
        vocab: Vocab,
        name: str = "pure_logistic_textcat",
        *,
        learning_rate: float = 0.001,
        max_iterations: int = 100,
        batch_size: int = 1000
    ):
        """
        Initialize the PureLogisticTextCategorizer.
        :param vocab: The vocabulary of the spaCy model
        :param name: The name of the pipeline component
        :param learning_rate: Learning rate for gradient descent
        :param max_iterations: Maximum iterations for training
        :param batch_size: Size of the training batch
        """
        self.vocab = vocab
        self.name = name
        self.learning_rate = learning_rate
        self.max_iterations = max_iterations
        self.batch_size = batch_size
        self.weights = None  # Initialize weights to None
        self.bias = None  # Initialize bias to None
        self._labels = set()  # Initialize labels set

        # Register the custom extensions in spaCy Doc object for handling scores
        if not Doc.has_extension("textcat_scores"):
            Doc.set_extension("textcat_scores", default={})
        if not Doc.has_extension("cats"):
            Doc.set_extension("cats", default={})

    def predict(self, docs: List[Doc]) -> List[Doc]:
        """
        Predict the categories for the given documents.
        :param docs: List of spaCy Doc objects to predict on
        :return: The same list of docs with textcat scores annotated
        """
        scores = self._predict_scores(docs)  # Get predicted scores
        self.set_annotations(docs, scores)  # Set the predictions on the docs
        return docs

    def _predict_scores(self, docs: List[Doc]) -> List[Dict[str, float]]:
        """
        Predict the scores for each document.
        :param docs: List of spaCy Doc objects
        :return: List of dictionaries with label scores for each doc
        """
        features = self._extract_features(docs)  # Extract features from the documents
        scores = []
        for doc_features in features:
            if self.weights is None:
                # If weights are not initialized, assign 0.5 (neutral probability) to each label
                doc_scores = {label: 0.5 for label in self.labels}
            else:
                # Calculate the logits and convert them to probabilities using the sigmoid function
                logits = np.dot(doc_features, self.weights) + self.bias
                probs = 1 / (1 + np.exp(-logits))
                # Store the scores for each label
                doc_scores = {
                    label: float(probs[i]) for i, label in enumerate(sorted(self.labels))
                }
            scores.append(doc_scores)
        return scores

    def update(
        self,
        examples: Iterable[Example],
        *,
        drop: float = 0.0,
        sgd=None,
        losses=None
    ) -> Dict[str, float]:
        """
        Update the model using the provided training examples.
        :param examples: Iterable of spaCy Example objects
        :param drop: Dropout rate (currently not used)
        :param sgd: Optional optimizer (currently not used)
        :param losses: Dictionary to track the model's loss
        :return: Updated loss dictionary
        """
        losses = {} if losses is None else losses
        docs = [eg.reference for eg in examples]
        features = self._extract_features(docs)
        sorted_labels = sorted(self.labels)
        labels = np.array([
            [eg.reference.cats.get(label, 0.0) for label in sorted_labels] for eg in examples
        ])

        # Initialize weights and bias if not already set
        if self.weights is None:
            n_features = len(features[0])
            self.weights = np.zeros((n_features, len(self.labels)))
            self.bias = np.zeros(len(self.labels))

        # Training loop
        total_loss = 0.0
        features = np.array(features)
        
        for _ in range(self.max_iterations):
            # Forward pass: calculate logits and probabilities
            logits = np.dot(features, self.weights) + self.bias
            probs = 1 / (1 + np.exp(-logits))

            # Calculate loss using binary cross-entropy
            loss = -np.mean(
                labels * np.log(probs + 1e-8) +
                (1 - labels) * np.log(1 - probs + 1e-8)
            )
            total_loss += loss

            # Backward pass: calculate gradients and update weights and bias
            d_probs = (probs - labels) / len(features)
            d_weights = np.dot(features.T, d_probs)
            d_bias = np.sum(d_probs, axis=0)

            # Update the weights and bias using gradient descent
            self.weights -= self.learning_rate * d_weights
            self.bias -= self.learning_rate * d_bias

        # Average loss over the iterations
        losses[self.name] = total_loss / self.max_iterations
        return losses

    def _extract_features(self, docs: List[Doc]) -> List[np.ndarray]:
        """
        Extract features from the documents.
        :param docs: List of spaCy Doc objects
        :return: List of feature arrays for each document
        """
        features = []
        for doc in docs:
            # Document vector as the main feature
            doc_vector = doc.vector

            # Additional length-based features
            n_tokens = len(doc)
            avg_token_length = (
                np.mean([len(token.text) for token in doc]) if n_tokens > 0 else 0
            )

            # Combine all features into a single feature vector
            combined_features = np.concatenate([
                doc_vector,
                [n_tokens / 100.0, avg_token_length / 10.0]  # Scale the features
            ])
            features.append(combined_features)
        return features

    @property
    def labels(self) -> set:
        """
        Get the current set of labels.
        :return: Set of labels
        """
        return self._labels

    @labels.setter
    def labels(self, value: Iterable[str]):
        """
        Set the labels for the categorizer and reset weights.
        :param value: Iterable of label strings
        """
        self._labels = set(value)
        # Reset weights and bias when labels change
        self.weights = None
        self.bias = None

    def set_annotations(self, docs: List[Doc], scores: List[Dict[str, float]]):
        """
        Set the scores on the documents.
        :param docs: List of spaCy Doc objects
        :param scores: List of score dictionaries for each document
        """
        for doc, score in zip(docs, scores):
            # Set the textcat_scores attribute
            doc._.textcat_scores = score
            # Set the cats attribute (for compatibility with binary classification)
            doc._.cats = score

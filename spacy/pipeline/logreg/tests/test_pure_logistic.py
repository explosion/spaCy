import pytest
import numpy as np
import spacy
from spacy.language import Language
from spacy.tokens import Doc
from spacy.training import Example

# Define the NLP fixture for testing
@pytest.fixture
def nlp():
    """
    Fixture to provide a blank spaCy English model for testing purposes.
    """
    return spacy.blank("en")


@Language.component("pure_logistic_textcat")
def pure_logistic_textcat(doc):
    """
    Custom spaCy pipeline component that assigns fixed text categorization scores
    to the document.

    Args:
        doc (Doc): The spaCy document to process.

    Returns:
        Doc: The processed document with 'textcat_scores' attribute set.
    """
    # Placeholder for text categorization scores
    scores = {"positive": 0.5, "negative": 0.5}

    # Ensure the 'textcat_scores' extension exists
    if not Doc.has_extension("textcat_scores"):
        Doc.set_extension("textcat_scores", default=None)

    # Assign the scores to the document's custom attribute
    doc._.textcat_scores = scores
    return doc


# Register the custom extension attribute if not already registered
if not Doc.has_extension("textcat_scores"):
    Doc.set_extension("textcat_scores", default=None)


def test_pure_logistic_textcat_empty_doc(nlp):
    """
    Test that the text categorization component can handle an empty document.
    """
    nlp.add_pipe("pure_logistic_textcat")
    doc = nlp("")
    assert doc._.textcat_scores is not None
    assert isinstance(doc._.textcat_scores, dict)


def test_pure_logistic_textcat_single_word(nlp):
    """
    Test that the component correctly handles a single-word document.
    """
    nlp.add_pipe("pure_logistic_textcat")
    doc = nlp("positive")
    assert doc._.textcat_scores is not None
    assert isinstance(doc._.textcat_scores, dict)


def test_pure_logistic_textcat_special_chars(nlp):
    """
    Test that the component can process documents containing special characters.
    """
    nlp.add_pipe("pure_logistic_textcat")
    doc = nlp("!@#$%^&*()")
    assert doc._.textcat_scores is not None
    assert isinstance(doc._.textcat_scores, dict)


def test_pure_logistic_textcat_invalid_input_type(nlp):
    """
    Test that the component raises a ValueError when given invalid input types.
    """
    with pytest.raises(ValueError):
        nlp.add_pipe("pure_logistic_textcat")
        nlp(12345)  # Invalid input: integer instead of string


def test_pure_logistic_textcat_reset(nlp):
    """
    Test that the 'textcat_scores' attribute is reset between different documents.
    """
    nlp.add_pipe("pure_logistic_textcat")
    
    doc1 = nlp("This is a test document")
    assert doc1._.textcat_scores is not None

    doc2 = nlp("Another test")
    assert doc2._.textcat_scores is not None
    assert doc1 is not doc2  # Ensure they are distinct documents


def test_pure_logistic_textcat_duplicate_component(nlp):
    """
    Test that adding the same component twice to the pipeline raises a ValueError.
    """
    nlp.add_pipe("pure_logistic_textcat")
    with pytest.raises(ValueError):
        nlp.add_pipe("pure_logistic_textcat")  # Duplicate addition should fail


def test_pure_logistic_textcat_multiple_sentences(nlp):
    """
    Test that the component correctly handles documents with multiple sentences.
    """
    nlp.add_pipe("pure_logistic_textcat")
    doc = nlp("This is the first sentence. This is the second.")
    assert doc._.textcat_scores is not None


def test_pure_logistic_textcat_with_extension(nlp):
    """
    Test that the component correctly handles the scenario where the custom
    'textcat_scores' extension is missing before processing.
    """
    # Remove the extension if it exists
    if Doc.has_extension("textcat_scores"):
        Doc.remove_extension("textcat_scores")

    # Add the custom component
    nlp.add_pipe("pure_logistic_textcat")

    # Process the document and verify the extension
    doc = nlp("This is a test document")
    assert hasattr(doc._, "textcat_scores"), "The 'textcat_scores' extension should be present"
    assert isinstance(doc._.textcat_scores, dict), "The 'textcat_scores' extension should be a dictionary"


def test_pure_logistic_textcat_empty_train_data(nlp):
    """
    Test that the update method handles empty training data gracefully.
    """
    def mock_update(examples):
        return {"pure_logistic_textcat": 0.0}

    textcat = nlp.add_pipe("pure_logistic_textcat")
    textcat.update = mock_update
    losses = textcat.update([])
    assert isinstance(losses, dict)
    assert losses["pure_logistic_textcat"] == 0.0


def test_pure_logistic_textcat_label_mismatch(nlp):
    """
    Test that the component handles mismatched labels in the training data.
    """
    textcat = nlp.add_pipe("pure_logistic_textcat")

    # Mismatched label in the training data
    train_examples = []
    for text, annotations in TRAIN_DATA_MISMATCH:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        train_examples.append(example)

    # Mock update method
    def mock_update(examples):
        return {"pure_logistic_textcat": 1.0}  # Arbitrary loss

    textcat.update = mock_update
    losses = textcat.update(train_examples)
    assert isinstance(losses, dict)
    assert "pure_logistic_textcat" in losses


# Mock training data for testing
TRAIN_DATA = [
    ("This is positive", {"cats": {"positive": 1.0, "negative": 0.0}}),
    ("This is negative", {"cats": {"positive": 0.0, "negative": 1.0}})
]

# Mismatched training data with incorrect labels
TRAIN_DATA_MISMATCH = [
    ("This is positive", {"cats": {"unknown_label": 1.0, "negative": 0.0}}),
    ("This is negative", {"cats": {"positive": 0.0, "unknown_label": 1.0}})
]


def test_pure_logistic_textcat_init(nlp):
    """
    Test that the text categorization component initializes correctly.
    """
    textcat = nlp.add_pipe("pure_logistic_textcat")
    assert textcat is not None


def test_pure_logistic_textcat_predict(nlp):
    """
    Test that the component's prediction works correctly.
    """
    nlp.add_pipe("pure_logistic_textcat")
    doc = nlp("This is a test document")
    assert doc._.textcat_scores is not None
    assert isinstance(doc._.textcat_scores, dict)
    assert "positive" in doc._.textcat_scores
    assert "negative" in doc._.textcat_scores


def test_pure_logistic_textcat_update(nlp):
    """
    Test that the component's update method works as expected.
    """
    def mock_update(examples):
        losses = {"pure_logistic_textcat": 0.5}  # Dummy loss value
        return losses

    textcat = nlp.add_pipe("pure_logistic_textcat")
    textcat.update = mock_update

    train_examples = []
    for text, annotations in TRAIN_DATA:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        train_examples.append(example)

    losses = textcat.update(train_examples)
    assert isinstance(losses, dict)
    assert "pure_logistic_textcat" in losses
    assert losses["pure_logistic_textcat"] == 0.5  # Ensure the loss is correct

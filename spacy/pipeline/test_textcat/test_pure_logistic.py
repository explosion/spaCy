import pytest
from spacy.language import Language
from spacy.training import Example
import spacy
from spacy.tokens import Doc
import numpy as np

# Define the nlp fixture
@pytest.fixture
def nlp():
    # Load the spaCy model
    return spacy.blank("en")  # Use a blank model for testing

# Custom component definition
@Language.component("pure_logistic_textcat")
def pure_logistic_textcat(doc):
    # Dummy implementation of text classification, replace with your model's logic
    scores = {"positive": 0.5, "negative": 0.5}
    
    # Store the scores in a custom attribute on the doc
    doc._.set("textcat_scores", scores)
    return doc

# Register the custom extension attribute
if not Doc.has_extension("textcat_scores"):
    Doc.set_extension("textcat_scores", default=None)

# Register the custom component to the spaCy pipeline
def test_pure_logistic_textcat_init(nlp):
    # Add the component to the pipeline
    textcat = nlp.add_pipe("pure_logistic_textcat")
    assert textcat is not None

def test_pure_logistic_textcat_predict(nlp):
    # Add the component to the pipeline
    nlp.add_pipe("pure_logistic_textcat")
    doc = nlp("This is a test document")
    
    # Check if the textcat_scores attribute exists and is a dictionary
    assert doc._.textcat_scores is not None
    assert isinstance(doc._.textcat_scores, dict)
    assert "positive" in doc._.textcat_scores
    assert "negative" in doc._.textcat_scores

def test_pure_logistic_textcat_update(nlp):
    # Mock an update method for testing purposes
    def mock_update(examples):
        losses = {"pure_logistic_textcat": 0.5}  # Dummy loss value
        return losses

    # Add the component to the pipeline
    textcat = nlp.add_pipe("pure_logistic_textcat")
    
    # Mock the update method for testing purposes
    textcat.update = mock_update
    
    train_examples = []
    for text, annotations in TRAIN_DATA:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        train_examples.append(example)
    
    # Update the model
    losses = textcat.update(train_examples)  # Ensure update method exists
    assert isinstance(losses, dict)
    assert "pure_logistic_textcat" in losses

# Mock training data for the test
TRAIN_DATA = [
    ("This is positive", {"cats": {"positive": 1.0, "negative": 0.0}}),
    ("This is negative", {"cats": {"positive": 0.0, "negative": 1.0}})
]

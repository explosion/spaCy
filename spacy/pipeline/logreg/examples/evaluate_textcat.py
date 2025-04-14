import spacy
from spacy.training import Example
from spacy.tokens import Doc 
from typing import Dict, List

# Import the custom logistic classifier
from pure_Logistic import make_pure_logistic_textcat


# Registering the custom extension 'textcat' to store predictions
if not Doc.has_extension("textcat"):
    Doc.set_extension("textcat", default={})


# Sample training and testing data
TRAIN_DATA = [
    ("This product is amazing! I love it.", {"cats": {"positive": 1.0, "negative": 0.0}}),
    ("The service was excellent and staff very friendly.", {"cats": {"positive": 1.0, "negative": 0.0}}),
    ("I'm really impressed with the quality.", {"cats": {"positive": 1.0, "negative": 0.0}}),
    ("Best purchase I've made in years!", {"cats": {"positive": 1.0, "negative": 0.0}}),
    ("The features work exactly as advertised.", {"cats": {"positive": 1.0, "negative": 0.0}}),
    ("This is terrible, complete waste of money.", {"cats": {"positive": 0.0, "negative": 1.0}}),
    ("Poor customer service, very disappointing.", {"cats": {"positive": 0.0, "negative": 1.0}}),
    ("The product broke after one week.", {"cats": {"positive": 0.0, "negative": 1.0}}),
    ("Would not recommend to anyone.", {"cats": {"positive": 0.0, "negative": 1.0}}),
    ("Save your money and avoid this.", {"cats": {"positive": 0.0, "negative": 1.0}})
]

TEST_DATA = [
    ("Great product, highly recommend!", {"cats": {"positive": 1.0, "negative": 0.0}}),
    ("Not worth the price at all.", {"cats": {"positive": 0.0, "negative": 1.0}}),
    ("Everything works perfectly.", {"cats": {"positive": 1.0, "negative": 0.0}}),
    ("Disappointed with the results.", {"cats": {"positive": 0.0, "negative": 1.0}})
]

def calculate_metrics(true_positives: int, true_negatives: int, false_positives: int, false_negatives: int) -> Dict[str, float]:
    """Calculate evaluation metrics based on counts."""
    total = true_positives + true_negatives + false_positives + false_negatives
    accuracy = (true_positives + true_negatives) / total if total > 0 else 0
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }

def evaluate_model(nlp, test_data):
    """Evaluate the model using the test data."""
    true_positives = true_negatives = false_positives = false_negatives = 0
    predictions = []
    
    for text, annotations in test_data:
        doc = nlp(text)
        true_cats = annotations["cats"]
        pred_cats = doc._.textcat  # Predictions from the custom model
        
        # Extract scores for 'positive' and 'negative'
        pred_positive_score = pred_cats["positive"] if "positive" in pred_cats else 0.0
        true_positive_score = true_cats.get("positive", 0.0)
        
        pred_positive = float(pred_positive_score) > 0.5
        true_positive = float(true_positive_score) > 0.5
        
        # Update counts based on predictions
        if true_positive and pred_positive:
            true_positives += 1
        elif not true_positive and not pred_positive:
            true_negatives += 1
        elif not true_positive and pred_positive:
            false_positives += 1
        else:
            false_negatives += 1
            
        predictions.append({
            "text": text,
            "true": "positive" if true_positive else "negative",
            "predicted": "positive" if pred_positive else "negative",
            "scores": pred_cats
        })
    
    metrics = calculate_metrics(true_positives, true_negatives, false_positives, false_negatives)
    return metrics, predictions


def main():
    try:
        print("Loading spaCy model...")
        nlp = spacy.load("en_core_web_lg")
    except OSError:
        print("Downloading spaCy model...")
        spacy.cli.download("en_core_web_lg")
        nlp = spacy.load("en_core_web_lg")
    
    print("Adding custom text categorizer...")
    config = {
        "learning_rate": 0.001,
        "max_iterations": 100,
        "batch_size": 1000
    }
    if "pure_logistic_textcat" not in nlp.pipe_names:
        textcat = nlp.add_pipe("pure_logistic_textcat", config=config)
        textcat.labels = {"positive", "negative"}
    
    print("Preparing training examples...")
    train_examples = []
    for text, annotations in TRAIN_DATA:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        train_examples.append(example)
    
    print("Training the model...")
    textcat = nlp.get_pipe("pure_logistic_textcat")
    losses = textcat.update(train_examples)
    print(f"Training losses: {losses}")
    
    print("\nEvaluating the model...")
    metrics, predictions = evaluate_model(nlp, TEST_DATA)
    
    print("\nEvaluation Metrics:")
    print(f"Accuracy:  {metrics['accuracy']:.3f}")
    print(f"Precision: {metrics['precision']:.3f}")
    print(f"Recall:    {metrics['recall']:.3f}")
    print(f"F1 Score:  {metrics['f1']:.3f}")
    
    print("\nDetailed Predictions:")
    for pred in predictions:
        print(f"\nText: {pred['text']}")
        print(f"True label: {pred['true']}")
        print(f"Predicted: {pred['predicted']}")
        print(f"Positive score: {pred['scores']['positive']:.3f}")
        print(f"Negative score: {pred['scores']['negative']:.3f}")

if __name__ == "__main__":
    main()

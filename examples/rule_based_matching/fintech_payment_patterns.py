import spacy

def main():
    """
    Demonstrate rule-based matching for FinTech domain entities using EntityRuler.
    Extracts payment schemes, UK sort codes, and account numbers.
    """
    # Load a blank English pipeline
    nlp = spacy.blank("en")

    # Add the EntityRuler to the pipeline
    ruler = nlp.add_pipe("entity_ruler")

    # Define FinTech-specific patterns
    patterns = [
        # Payment Schemes
        {"label": "PAYMENT_SCHEME", "pattern": "CHAPS"},
        {"label": "PAYMENT_SCHEME", "pattern": "BACS"},
        {"label": "PAYMENT_SCHEME", "pattern": "SWIFT"},
        {"label": "PAYMENT_SCHEME", "pattern": "SEPA"},
        
        # UK Sort Code (e.g., 20-45-14 or 204514)
        {"label": "SORT_CODE", "pattern": [{"SHAPE": "dd"}, {"TEXT": "-"}, {"SHAPE": "dd"}, {"TEXT": "-"}, {"SHAPE": "dd"}]},
        {"label": "SORT_CODE", "pattern": [{"SHAPE": "dddddd"}]},
        
        # Standard Account Number (8 digits)
        {"label": "ACCOUNT_NUMBER", "pattern": [{"SHAPE": "dddddddd"}]}
    ]

    ruler.add_patterns(patterns)

    # Test the pipeline on a sample financial operations text
    text = "The settlement was routed via CHAPS to account 87654321, sort code 40-47-59."
    doc = nlp(text)

    print(f"{'Entity Text':<15} {'Label':<15}")
    print("-" * 30)
    for ent in doc.ents:
        print(f"{ent.text:<15} {ent.label_:<15}")

if __name__ == "__main__":
    main()

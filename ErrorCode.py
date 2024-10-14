# Process finished with exit code -1073741819 (0xC0000005) #13659
# I have tried the below solution. Please check it once if this helps please let me know.

import spacy

# Load the SpaCy language model
nlp = spacy.load('en_core_web_lg')

# Open the file and process each line
with open('data/1971 Davis Cup.txt', encoding='utf-8') as file:
    for line in file:
        line = line.strip()
        if not line:  # Skip empty lines
            continue
        
        doc = nlp(line)  # Process the line with SpaCy
        tokens = [token.text for token in doc]  # Extract tokens

        dependencies = set()
        for token in doc:
            for child in token.children:
                dependencies.add((token.i, token.dep_, child.i))  # Collect dependency relations

        print(f"Tokens: {tokens}")  # Display tokens
        print(f"Dependencies: {dependencies}")  # Display dependency relations

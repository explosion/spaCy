import spacy

nlp = spacy.blank("si")

text = "එහි අරමුණු කිහිපයකි. ඒවා අතර;"
doc = nlp(text)

print(f"Total tokens: {len(doc)}")
print()
for i, token in enumerate(doc):
    print(f"{i+1:>3}  {token.text}")
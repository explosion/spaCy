'''
Match a dependency pattern. See https://github.com/explosion/spaCy/pull/1120

We start by creating a DependencyTree for the Doc. This class models the document
dependency tree. Then we compile the query into a Pattern using the PatternParser.
The syntax is quite simple:

we define a node named 'fox', that must match in the dep tree a token
whose orth_ is 'fox'. an anonymous token whose lemma is 'quick' must have fox
as parent, with a dep_ matching the regex am.* another anonymous token whose
orth_ matches the regex brown|yellow has fox as parent, with whathever dep_
DependencyTree.match returns a list of PatternMatch. Notice that we can assign
names to anonymous or defined nodes ([word:fox]=f). We can get the Token mapped
to the fox node using match['f'].
'''
import spacy
from spacy.pattern import PatternParser, DependencyTree

nlp = spacy.load('en')
doc = nlp("The quick brown fox jumped over the lazy dog.")
tree = DependencyTree(doc)

query = """fox [word:fox]=f
           [lemma:quick]=q >/am.*/ fox
           [word:/brown|yellow/] > fox"""

pattern = PatternParser.parse(query)
matches = tree.match(pattern)

assert len(matches) == 1
match = matches[0]

assert match['f'] == doc[3]

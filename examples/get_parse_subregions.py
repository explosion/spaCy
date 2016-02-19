"""Issue #252

Question:

In the documents and tutorials the main thing I haven't found is examples on how to break sentences down into small sub thoughts/chunks. The noun_chunks is handy, but having examples on using the token.head to find small (near-complete) sentence chunks would be neat.

Lets take the example sentence on https://displacy.spacy.io/displacy/index.html

displaCy uses CSS and JavaScript to show you how computers understand language
This sentence has two main parts (XCOMP & CCOMP) according to the breakdown:

[displaCy] uses CSS and Javascript [to + show]
&
show you how computers understand [language]
I'm assuming that we can use the token.head to build these groups. In one of your examples you had the following function.

def dependency_labels_to_root(token):
    '''Walk up the syntactic tree, collecting the arc labels.'''
    dep_labels = []
    while token.head is not token:
        dep_labels.append(token.dep)
        token = token.head
    return dep_labels
"""
from __future__ import print_function, unicode_literals

# Answer:
# The easiest way is to find the head of the subtree you want, and then use the
# `.subtree`, `.children`, `.lefts` and `.rights` iterators. `.subtree` is the
# one that does what you're asking for most directly:

from spacy.en import English
nlp = English()

doc = nlp(u'displaCy uses CSS and JavaScript to show you how computers understand language')
for word in doc:
    if word.dep_ in ('xcomp', 'ccomp'):
        print(''.join(w.text_with_ws for w in word.subtree))

# It'd probably be better for `word.subtree` to return a `Span` object instead 
# of a generator over the tokens. If you want the `Span` you can get it via the 
# `.right_edge` and `.left_edge` properties. The `Span` object is nice because 
# you can easily get a vector, merge it, etc.

doc = nlp(u'displaCy uses CSS and JavaScript to show you how computers understand language')
for word in doc:
    if word.dep_ in ('xcomp', 'ccomp'):
        subtree_span = doc[word.left_edge.i : word.right_edge.i + 1]
        print(subtree_span.text, '|', subtree_span.root.text)
        print(subtree_span.similarity(doc))
        print(subtree_span.similarity(subtree_span.root))


# You might also want to select a head, and then select a start and end position by
# walking along its children. You could then take the `.left_edge` and `.right_edge`
# of those tokens, and use it to calculate a span.




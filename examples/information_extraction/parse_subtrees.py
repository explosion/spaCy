#!/usr/bin/env python
# coding: utf8
"""This example shows how to navigate the parse tree including subtrees
attached to a word.

Based on issue #252:
"In the documents and tutorials the main thing I haven't found is
examples on how to break sentences down into small sub thoughts/chunks. The
noun_chunks is handy, but having examples on using the token.head to find small
(near-complete) sentence chunks would be neat. Lets take the example sentence:
"displaCy uses CSS and JavaScript to show you how computers understand language"

This sentence has two main parts (XCOMP & CCOMP) according to the breakdown:
[displaCy] uses CSS and Javascript [to + show]
show you how computers understand [language]

I'm assuming that we can use the token.head to build these groups."

Compatible with: spaCy v2.0.0+
"""
from __future__ import unicode_literals, print_function

import plac
import spacy


@plac.annotations(
    model=("Model to load", "positional", None, str))
def main(model='en_core_web_sm'):
    nlp = spacy.load(model)
    print("Loaded model '%s'" % model)

    doc = nlp("displaCy uses CSS and JavaScript to show you how computers "
               "understand language")

    # The easiest way is to find the head of the subtree you want, and then use
    # the `.subtree`, `.children`, `.lefts` and `.rights` iterators. `.subtree`
    # is the one that does what you're asking for most directly:
    for word in doc:
        if word.dep_ in ('xcomp', 'ccomp'):
            print(''.join(w.text_with_ws for w in word.subtree))

    # It'd probably be better for `word.subtree` to return a `Span` object
    # instead of a generator over the tokens. If you want the `Span` you can
    # get it via the `.right_edge` and `.left_edge` properties. The `Span`
    # object is nice because you can easily get a vector, merge it, etc.
    for word in doc:
        if word.dep_ in ('xcomp', 'ccomp'):
            subtree_span = doc[word.left_edge.i : word.right_edge.i + 1]
            print(subtree_span.text, '|', subtree_span.root.text)

    # You might also want to select a head, and then select a start and end
    # position by walking along its children. You could then take the
    # `.left_edge` and `.right_edge` of those tokens, and use it to calculate
    # a span.

if __name__ == '__main__':
    plac.call(main)

    # Expected output:
    # to show you how computers understand language
    # how computers understand language
    # to show you how computers understand language | show
    # how computers understand language | understand

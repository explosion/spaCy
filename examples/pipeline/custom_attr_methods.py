#!/usr/bin/env python
# coding: utf-8
"""This example contains several snippets of methods that can be set via custom
Doc, Token or Span attributes in spaCy v2.0. Attribute methods act like
they're "bound" to the object and are partially applied – i.e. the object
they're called on is passed in as the first argument.

* Custom pipeline components: https://spacy.io//usage/processing-pipelines#custom-components

Compatible with: spaCy v2.0.0+
"""
from __future__ import unicode_literals, print_function

import plac
from spacy.lang.en import English
from spacy.tokens import Doc, Span
from spacy import displacy
from pathlib import Path


@plac.annotations(
    output_dir=("Output directory for saved HTML", "positional", None, Path))
def main(output_dir=None):
    nlp = English()  # start off with blank English class

    Doc.set_extension('overlap', method=overlap_tokens)
    doc1 = nlp(u"Peach emoji is where it has always been.")
    doc2 = nlp(u"Peach is the superior emoji.")
    print("Text 1:", doc1.text)
    print("Text 2:", doc2.text)
    print("Overlapping tokens:", doc1._.overlap(doc2))

    Doc.set_extension('to_html', method=to_html)
    doc = nlp(u"This is a sentence about Apple.")
    # add entity manually for demo purposes, to make it work without a model
    doc.ents = [Span(doc, 5, 6, label=nlp.vocab.strings['ORG'])]
    print("Text:", doc.text)
    doc._.to_html(output=output_dir, style='ent')


def to_html(doc, output='/tmp', style='dep'):
    """Doc method extension for saving the current state as a displaCy
    visualization.
    """
    # generate filename from first six non-punct tokens
    file_name = '-'.join([w.text for w in doc[:6] if not w.is_punct]) + '.html'
    html = displacy.render(doc, style=style, page=True)  # render markup
    if output is not None:
        output_path = Path(output)
        if not output_path.exists():
            output_path.mkdir()
        output_file = Path(output) / file_name
        output_file.open('w', encoding='utf-8').write(html)  # save to file
        print('Saved HTML to {}'.format(output_file))
    else:
        print(html)


def overlap_tokens(doc, other_doc):
    """Get the tokens from the original Doc that are also in the comparison Doc.
    """
    overlap = []
    other_tokens = [token.text for token in other_doc]
    for token in doc:
        if token.text in other_tokens:
            overlap.append(token)
    return overlap


if __name__ == '__main__':
    plac.call(main)

    # Expected output:
    # Text 1: Peach emoji is where it has always been.
    # Text 2: Peach is the superior emoji.
    # Overlapping tokens: [Peach, emoji, is, .]

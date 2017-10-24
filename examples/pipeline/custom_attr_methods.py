# coding: utf-8
"""This example contains several snippets of methods that can be set via custom
Doc, Token or Span attributes in spaCy v2.0. Attribute methods act like
they're "bound" to the object and are partially applied – i.e. the object
they're called on is passed in as the first argument."""
from __future__ import unicode_literals

from spacy.lang.en import English
from spacy.tokens import Doc, Span
from spacy import displacy
from pathlib import Path


def to_html(doc, output='/tmp', style='dep'):
    """Doc method extension for saving the current state as a displaCy
    visualization.
    """
    # generate filename from first six non-punct tokens
    file_name = '-'.join([w.text for w in doc[:6] if not w.is_punct]) + '.html'
    output_path = Path(output) / file_name
    html = displacy.render(doc, style=style, page=True)  # render markup
    output_path.open('w', encoding='utf-8').write(html)  # save to file
    print('Saved HTML to {}'.format(output_path))


Doc.set_extension('to_html', method=to_html)

nlp = English()
doc = nlp(u"This is a sentence about Apple.")
# add entity manually for demo purposes, to make it work without a model
doc.ents = [Span(doc, 5, 6, label=nlp.vocab.strings['ORG'])]
doc._.to_html(style='ent')


def overlap_tokens(doc, other_doc):
    """Get the tokens from the original Doc that are also in the comparison Doc.
    """
    overlap = []
    other_tokens = [token.text for token in other_doc]
    for token in doc:
        if token.text in other_tokens:
            overlap.append(token)
    return overlap


Doc.set_extension('overlap', method=overlap_tokens)

nlp = English()
doc1 = nlp(u"Peach emoji is where it has always been.")
doc2 = nlp(u"Peach is the superior emoji.")
tokens = doc1._.overlap(doc2)
print(tokens)

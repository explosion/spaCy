#!/usr/bin/env python
# coding: utf8
"""Example of a spaCy v2.0 pipeline component that sets entity annotations
based on list of single or multiple-word company names. Companies are
labelled as ORG and their spans are merged into one token. Additionally,
._.has_tech_org and ._.is_tech_org is set on the Doc/Span and Token
respectively.

* Custom pipeline components: https://spacy.io//usage/processing-pipelines#custom-components

Compatible with: spaCy v2.0.0+
"""
from __future__ import unicode_literals, print_function

import plac
from spacy.lang.en import English
from spacy.matcher import PhraseMatcher
from spacy.tokens import Doc, Span, Token


@plac.annotations(
    text=("Text to process", "positional", None, str),
    companies=("Names of technology companies", "positional", None, str))
def main(text="Alphabet Inc. is the company behind Google.", *companies):
    # For simplicity, we start off with only the blank English Language class
    # and no model or pre-defined pipeline loaded.
    nlp = English()
    if not companies:  # set default companies if none are set via args
        companies = ['Alphabet Inc.', 'Google', 'Netflix', 'Apple']  # etc.
    component = TechCompanyRecognizer(nlp, companies)  # initialise component
    nlp.add_pipe(component, last=True)  # add last to the pipeline

    doc = nlp(text)
    print('Pipeline', nlp.pipe_names)  # pipeline contains component name
    print('Tokens', [t.text for t in doc])  # company names from the list are merged
    print('Doc has_tech_org', doc._.has_tech_org)  # Doc contains tech orgs
    print('Token 0 is_tech_org', doc[0]._.is_tech_org)  # "Alphabet Inc." is a tech org
    print('Token 1 is_tech_org', doc[1]._.is_tech_org)  # "is" is not
    print('Entities', [(e.text, e.label_) for e in doc.ents])  # all orgs are entities


class TechCompanyRecognizer(object):
    """Example of a spaCy v2.0 pipeline component that sets entity annotations
    based on list of single or multiple-word company names. Companies are
    labelled as ORG and their spans are merged into one token. Additionally,
    ._.has_tech_org and ._.is_tech_org is set on the Doc/Span and Token
    respectively."""
    name = 'tech_companies'  # component name, will show up in the pipeline

    def __init__(self, nlp, companies=tuple(), label='ORG'):
        """Initialise the pipeline component. The shared nlp instance is used
        to initialise the matcher with the shared vocab, get the label ID and
        generate Doc objects as phrase match patterns.
        """
        self.label = nlp.vocab.strings[label]  # get entity label ID

        # Set up the PhraseMatcher – it can now take Doc objects as patterns,
        # so even if the list of companies is long, it's very efficient
        patterns = [nlp(org) for org in companies]
        self.matcher = PhraseMatcher(nlp.vocab)
        self.matcher.add('TECH_ORGS', None, *patterns)

        # Register attribute on the Token. We'll be overwriting this based on
        # the matches, so we're only setting a default value, not a getter.
        Token.set_extension('is_tech_org', default=False)

        # Register attributes on Doc and Span via a getter that checks if one of
        # the contained tokens is set to is_tech_org == True.
        Doc.set_extension('has_tech_org', getter=self.has_tech_org)
        Span.set_extension('has_tech_org', getter=self.has_tech_org)

    def __call__(self, doc):
        """Apply the pipeline component on a Doc object and modify it if matches
        are found. Return the Doc, so it can be processed by the next component
        in the pipeline, if available.
        """
        matches = self.matcher(doc)
        spans = []  # keep the spans for later so we can merge them afterwards
        for _, start, end in matches:
            # Generate Span representing the entity & set label
            entity = Span(doc, start, end, label=self.label)
            spans.append(entity)
            # Set custom attribute on each token of the entity
            for token in entity:
                token._.set('is_tech_org', True)
            # Overwrite doc.ents and add entity – be careful not to replace!
            doc.ents = list(doc.ents) + [entity]
        for span in spans:
            # Iterate over all spans and merge them into one token. This is done
            # after setting the entities – otherwise, it would cause mismatched
            # indices!
            span.merge()
        return doc  # don't forget to return the Doc!

    def has_tech_org(self, tokens):
        """Getter for Doc and Span attributes. Returns True if one of the tokens
        is a tech org. Since the getter is only called when we access the
        attribute, we can refer to the Token's 'is_tech_org' attribute here,
        which is already set in the processing step."""
        return any([t._.get('is_tech_org') for t in tokens])


if __name__ == '__main__':
    plac.call(main)

    # Expected output:
    # Pipeline ['tech_companies']
    # Tokens ['Alphabet Inc.', 'is', 'the', 'company', 'behind', 'Google', '.']
    # Doc has_tech_org True
    # Token 0 is_tech_org True
    # Token 1 is_tech_org False
    # Entities [('Alphabet Inc.', 'ORG'), ('Google', 'ORG')]

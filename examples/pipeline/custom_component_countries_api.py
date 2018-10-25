#!/usr/bin/env python
# coding: utf8
"""Example of a spaCy v2.0 pipeline component that requests all countries via
the REST Countries API, merges country names into one token, assigns entity
labels and sets attributes on country tokens, e.g. the capital and lat/lng
coordinates. Can be extended with more details from the API.

* REST Countries API: https://restcountries.eu (Mozilla Public License MPL 2.0)
* Custom pipeline components: https://spacy.io//usage/processing-pipelines#custom-components

Compatible with: spaCy v2.0.0+
Prerequisites: pip install requests
"""
from __future__ import unicode_literals, print_function

import requests
import plac
from spacy.lang.en import English
from spacy.matcher import PhraseMatcher
from spacy.tokens import Doc, Span, Token


def main():
    # For simplicity, we start off with only the blank English Language class
    # and no model or pre-defined pipeline loaded.
    nlp = English()
    rest_countries = RESTCountriesComponent(nlp)  # initialise component
    nlp.add_pipe(rest_countries) # add it to the pipeline
    doc = nlp(u"Some text about Colombia and the Czech Republic")
    print('Pipeline', nlp.pipe_names)  # pipeline contains component name
    print('Doc has countries', doc._.has_country)  # Doc contains countries
    for token in doc:
        if token._.is_country:
            print(token.text, token._.country_capital, token._.country_latlng,
                token._.country_flag)  # country data
    print('Entities', [(e.text, e.label_) for e in doc.ents])  # entities


class RESTCountriesComponent(object):
    """spaCy v2.0 pipeline component that requests all countries via
    the REST Countries API, merges country names into one token, assigns entity
    labels and sets attributes on country tokens.
    """
    name = 'rest_countries' # component name, will show up in the pipeline

    def __init__(self, nlp, label='GPE'):
        """Initialise the pipeline component. The shared nlp instance is used
        to initialise the matcher with the shared vocab, get the label ID and
        generate Doc objects as phrase match patterns.
        """
        # Make request once on initialisation and store the data
        r = requests.get('https://restcountries.eu/rest/v2/all')
        r.raise_for_status()  # make sure requests raises an error if it fails
        countries = r.json()

        # Convert API response to dict keyed by country name for easy lookup
        # This could also be extended using the alternative and foreign language
        # names provided by the API
        self.countries = {c['name']: c for c in countries}
        self.label = nlp.vocab.strings[label]  # get entity label ID

        # Set up the PhraseMatcher with Doc patterns for each country name
        patterns = [nlp(c) for c in self.countries.keys()]
        self.matcher = PhraseMatcher(nlp.vocab)
        self.matcher.add('COUNTRIES', None, *patterns)

        # Register attribute on the Token. We'll be overwriting this based on
        # the matches, so we're only setting a default value, not a getter.
        # If no default value is set, it defaults to None.
        Token.set_extension('is_country', default=False)
        Token.set_extension('country_capital', default=False)
        Token.set_extension('country_latlng', default=False)
        Token.set_extension('country_flag', default=False)

        # Register attributes on Doc and Span via a getter that checks if one of
        # the contained tokens is set to is_country == True.
        Doc.set_extension('has_country', getter=self.has_country)
        Span.set_extension('has_country', getter=self.has_country)


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
            # Can be extended with other data returned by the API, like
            # currencies, country code, flag, calling code etc.
            for token in entity:
                token._.set('is_country', True)
                token._.set('country_capital', self.countries[entity.text]['capital'])
                token._.set('country_latlng', self.countries[entity.text]['latlng'])
                token._.set('country_flag', self.countries[entity.text]['flag'])
            # Overwrite doc.ents and add entity – be careful not to replace!
            doc.ents = list(doc.ents) + [entity]
        for span in spans:
            # Iterate over all spans and merge them into one token. This is done
            # after setting the entities – otherwise, it would cause mismatched
            # indices!
            span.merge()
        return doc  # don't forget to return the Doc!

    def has_country(self, tokens):
        """Getter for Doc and Span attributes. Returns True if one of the tokens
        is a country. Since the getter is only called when we access the
        attribute, we can refer to the Token's 'is_country' attribute here,
        which is already set in the processing step."""
        return any([t._.get('is_country') for t in tokens])


if __name__ == '__main__':
    plac.call(main)

    # Expected output:
    # Pipeline ['rest_countries']
    # Doc has countries True
    # Colombia Bogotá [4.0, -72.0] https://restcountries.eu/data/col.svg
    # Czech Republic Prague [49.75, 15.5] https://restcountries.eu/data/cze.svg
    # Entities [('Colombia', 'GPE'), ('Czech Republic', 'GPE')]

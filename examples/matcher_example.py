from __future__ import unicode_literals, print_function

import spacy.en
import spacy.matcher
from spacy.attrs import ORTH, TAG, LOWER, IS_ALPHA, FLAG63

import plac


def main():
    nlp = spacy.en.English()
    example = u"I prefer Siri to Google Now. I'll google now to find out how the google now service works."
    before = nlp(example)
    print("Before")
    for ent in before.ents:
        print(ent.text, ent.label_, [w.tag_ for w in ent])
    # Output:
    # Google ORG [u'NNP']
    # google ORG [u'VB']
    # google ORG [u'NNP']
    nlp.matcher.add(
        "GoogleNow", # Entity ID: Not really used at the moment.
        "PRODUCT",   # Entity type: should be one of the types in the NER data
        {"wiki_en": "Google_Now"}, # Arbitrary attributes. Currently unused.
        [  # List of patterns that can be Surface Forms of the entity

            # This Surface Form matches "Google Now", verbatim
            [ # Each Surface Form is a list of Token Specifiers.
                { # This Token Specifier matches tokens whose orth field is "Google"
                    ORTH: "Google"
                },
                { # This Token Specifier matches tokens whose orth field is "Now"
                    ORTH: "Now"
                }
            ],
            [ # This Surface Form matches "google now", verbatim, and requires
              # "google" to have the NNP tag. This helps prevent the pattern from
              # matching cases like "I will google now to look up the time"
                {
                    ORTH: "google",
                    TAG: "NNP"
                },
                {
                    ORTH: "now"
                }
            ]
        ]
    )
    after = nlp(example)
    print("After")
    for ent in after.ents:
        print(ent.text, ent.label_, [w.tag_ for w in ent])
    # Output
    # Google Now PRODUCT [u'NNP', u'RB']
    # google ORG [u'VB']
    # google now PRODUCT [u'NNP', u'RB']
    #
    # You can customize attribute values in the lexicon, and then refer to the
    # new attributes in your Token Specifiers.
    # This is particularly good for word-set membership.
    # 
    australian_capitals = ['Brisbane', 'Sydney', 'Canberra', 'Melbourne', 'Hobart',
                           'Darwin', 'Adelaide', 'Perth']
    # Internally, the tokenizer immediately maps each token to a pointer to a 
    # LexemeC struct. These structs hold various features, e.g. the integer IDs
    # of the normalized string forms.
    # For our purposes, the key attribute is a 64-bit integer, used as a bit field.
    # spaCy currently only uses 12 of the bits for its built-in features, so
    # the others are available for use. It's best to use the higher bits, as
    # future versions of spaCy may add more flags. For instance, we might add
    # a built-in IS_MONTH flag, taking up FLAG13. So, we bind our user-field to
    # FLAG63 here.
    is_australian_capital = FLAG63
    # Now we need to set the flag value. It's False on all tokens by default,
    # so we just need to set it to True for the tokens we want.
    # Here we iterate over the strings, and set it on only the literal matches.
    for string in australian_capitals:
        lexeme = nlp.vocab[string]
        lexeme.set_flag(is_australian_capital, True)
    print('Sydney', nlp.vocab[u'Sydney'].check_flag(is_australian_capital))
    print('sydney', nlp.vocab[u'sydney'].check_flag(is_australian_capital))
    # If we want case-insensitive matching, we have to be a little bit more
    # round-about, as there's no case-insensitive index to the vocabulary. So
    # we have to iterate over the vocabulary.
    # We'll be looking up attribute IDs in this set a lot, so it's good to pre-build it
    target_ids = {nlp.vocab.strings[s.lower()] for s in australian_capitals}
    for lexeme in nlp.vocab:
        if lexeme.lower in target_ids:
            lexeme.set_flag(is_australian_capital, True)
    print('Sydney', nlp.vocab[u'Sydney'].check_flag(is_australian_capital))
    print('sydney', nlp.vocab[u'sydney'].check_flag(is_australian_capital))
    print('SYDNEY', nlp.vocab[u'SYDNEY'].check_flag(is_australian_capital))
    # Output
    # Sydney True
    # sydney False
    # Sydney True
    # sydney True
    # SYDNEY True
    #
    # The key thing to note here is that we're setting these attributes once,
    # over the vocabulary --- and then reusing them at run-time. This means the
    # amortized complexity of anything we do this way is going to be O(1). You
    # can match over expressions that need to have sets with tens of thousands
    # of values, e.g. "all the street names in Germany", and you'll still have
    # O(1) complexity. Most regular expression algorithms don't scale well to
    # this sort of problem.
    #
    # Now, let's use this in a pattern
    nlp.matcher.add("AuCitySportsTeam", "ORG", {},
        [
            [
                {LOWER: "the"},
                {is_australian_capital: True},
                {TAG: "NNS"}
            ],
            [
                {LOWER: "the"},
                {is_australian_capital: True},
                {TAG: "NNPS"}
            ],
            [
                {LOWER: "the"},
                {IS_ALPHA: True}, # Allow a word in between, e.g. The Western Sydney
                {is_australian_capital: True},
                {TAG: "NNS"}
            ],
            [
                {LOWER: "the"},
                {IS_ALPHA: True}, # Allow a word in between, e.g. The Western Sydney
                {is_australian_capital: True},
                {TAG: "NNPS"}
            ]
        ])
    doc = nlp(u'The pattern should match the Brisbane Broncos and the South Darwin Spiders, but not the Colorado Boulders')
    for ent in doc.ents:
        print(ent.text, ent.label_)
    # Output
    # the Brisbane Broncos ORG
    # the South Darwin Spiders ORG


# Output
# Before
# Google ORG [u'NNP']
# google ORG [u'VB']
# google ORG [u'NNP']
# After
# Google Now PRODUCT [u'NNP', u'RB']
# google ORG [u'VB']
# google now PRODUCT [u'NNP', u'RB']
# Sydney True
# sydney False
# Sydney True
# sydney True
# SYDNEY True
# the Brisbane Broncos ORG
# the South Darwin Spiders ORG

if __name__ == '__main__':
    main()
    

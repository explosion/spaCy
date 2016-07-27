.. image:: https://travis-ci.org/spacy-io/spaCy.svg?branch=master
    :target: https://travis-ci.org/spacy-io/spaCy

==============================
spaCy: Industrial-strength NLP
==============================

spaCy is a library for advanced natural language processing in Python and Cython.

Documentation and details: https://spacy.io/

spaCy is built on the very latest research, but it isn't researchware.  It was
designed from day 1 to be used in real products. It's commercial open-source
software, released under the MIT license.

Features
--------

* Labelled dependency parsing (91.8% accuracy on OntoNotes 5)

* Named entity recognition (82.6% accuracy on OntoNotes 5)

* Part-of-speech tagging (97.1% accuracy on OntoNotes 5)

* Easy to use word vectors

* All strings mapped to integer IDs

* Export to numpy data arrays

* Alignment maintained to original string, ensuring easy mark up calculation

* Range of easy-to-use orthographic features.

* No pre-processing required. spaCy takes raw text as input, warts and newlines and all.

Top Peformance
--------------

* Fastest in the world: <50ms per document.  No faster system has ever been
  announced.

* Accuracy within 1% of the current state of the art on all tasks performed
  (parsing, named entity recognition, part-of-speech tagging).  The only more
  accurate systems are an order of magnitude slower or more.

Supports
--------

* CPython 2.6, 2.7, 3.3, 3.4, 3.5 (only 64 bit)
* OSX
* Linux
* Windows (Cygwin, MinGW, Visual Studio)


2016-05-0 0.101.0: Fixed German model
-------------------------------------

* Fixed bug that prevented German parses from being deprojectivised.

* Bug fixes to sentence boundary detection.

* Add rich comparison methods to the Lexeme class.

* Add missing Doc.has_vector and Span.has_vector properties.

* Add missing Span.sent property.


2016-05-05 v0.100.7: German!
----------------------------

spaCy finally supports another language, in addition to English. We're lucky to have Wolfgang Seeker on the team, and the new German model is just the beginning.
Now that there are multiple languages, you should consider loading spaCy via the load() function. This function also makes it easier to load extra word vector data for English:

.. code:: python

    import spacy
    en_nlp = spacy.load('en', vectors='en_glove_cc_300_1m_vectors')
    de_nlp = spacy.load('de')
    
To support use of the load function, there are also two new helper functions: spacy.get_lang_class and spacy.set_lang_class.
Once the German model is loaded, you can use it just like the English model:

.. code:: python

    doc = nlp(u'''Wikipedia ist ein Projekt zum Aufbau einer Enzyklopädie aus freien Inhalten, zu dem du mit deinem Wissen beitragen kannst. Seit Mai 2001 sind 1.936.257 Artikel in deutscher Sprache entstanden.''')
    
    for sent in doc.sents:
        print(sent.root.text, sent.root.n_lefts, sent.root.n_rights)
    
    # (u'ist', 1, 2)
    # (u'sind', 1, 3)
    
The German model provides tokenization, POS tagging, sentence boundary detection, syntactic dependency parsing, recognition of organisation, location and person entities, and word vector representations trained on a mix of open subtitles and Wikipedia data. It doesn't yet provide lemmatisation or morphological analysis, and it doesn't yet recognise numeric entities such as numbers and dates.

Bugfixes
--------

* spaCy < 0.100.7 had a bug in the semantics of the Token.__str__ and Token.__unicode__ built-ins: they included a trailing space.
* Improve handling of "infixed" hyphens. Previously the tokenizer struggled with multiple hyphens, such as "well-to-do".

* Improve handling of periods after mixed-case tokens

* Improve lemmatization for English special-case tokens

* Fix bug that allowed spaces to be treated as heads in the syntactic parse

* Fix bug that led to inconsistent sentence boundaries before and after serialisation.

* Fix bug from deserialising untagged documents.

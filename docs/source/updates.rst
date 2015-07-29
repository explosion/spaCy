Updates
=======

To update your installation:

.. code:: bash

    $ pip install --upgrade spacy
    $ python -m spacy.en.download all

Most updates ship a new model, so you will usually have to redownload the data.

2015-07-28 v0.89
----------------

Major update!

* Support efficient binary serialization.  The dependency tree,
  part-of-speech tags, named entities, tokenization and text can be dumped to a
  byte string smaller than the original text representation.  Serialization is
  lossless, so there's no need to separately store the original text.

  Serialize:
    
  .. code-block:: python

      byte_string = doc.to_bytes()

  Deserialize by first creating a Doc object, and then loading the bytes:
  
  .. code-block:: python
      
      doc = Doc(nlp.vocab)
      doc.from_bytes(byte_string)

  If you have a binary file with several parses saved, you can iterate over
  them using the staticmethod `Doc.read_bytes`. Putting it all together:

  .. code-block:: python

      import codecs

      from spacy.en import English

      def serialize(nlp, texts, out_loc):
          with open(out_loc, 'wb') as out_file:
              for text in texts:
                  doc = nlp(text)
                  out_file.write(doc.to_bytes())

      def deserialize(nlp, file_loc):
          docs = []
          with open(file_loc, 'rb') as read_file:
              for byte_string in Doc.read_bytes(read_file, 'rb')):
                  doc = Doc(nlp.vocab).from_bytes(byte_string)
                  docs.append(doc)
          return docs


  Full tutorial coming soon.


* Fix probability estimates, and base them off counts from the 2015 Reddit Comments
  dump.  The probability estimates are now very reliable, and out-of-vocabulary
  words now receive an accurate smoothed probability estimate.

* Fix regression in parse times on very long texts. Recent versions were
  calculating parse features in a way that was polynomial in input length. 

* Allow slicing into the Doc object, so that you can do e.g. doc[2:4]. Returns
  a Span object.

* Add tag SP (coarse tag SPACE) for whitespace tokens.  Fix bug where
  whitespace was sometimes marked as an entity.

* Reduce memory usage. Memory usage now under 2GB per process.

* Rename :code:`Span.head` to :code:`Span.root`, fix its documentation, and make
  it more efficient.  I considered adding Span.head, Span.dep and Span.dep\_ as
  well, but for now I leave these as accessible via :code:`Span.root.head`,
  :code:`Span.head.dep`, and :code:`Span.head.dep\_`, to keep the API smaller.  

* Add boolean features to Token and Lexeme objects.

* Main parse function now marked **nogil**. This
  means I'll be able to add a Worker class that allows multi-threaded
  processing.  This will be available in the next version.  In the meantime,
  you should continue to use multiprocessing for parallelization.


2015-07-08 v0.88
----------------

Refactoring release.

If you have the data for v0.87, you don't need to redownload the data for this
release.

* You can now set tag=False, parse=False or entity=False when creating the pipleine,
  to disable some of the models. See the documentation for details.
* Models no longer lazy-loaded.
* Warning emitted when parse=True or entity=True but model not loaded.
* Rename the tokens.Tokens class to tokens.Doc. An alias has been made to assist
  backwards compatibility, but you should update your code to refer to the new
  class name.
* Various bits of internal refactoring


2015-07-01 v0.87
----------------

* Changed weights data structure. Memory use should be reduced 30-40%.
* Fixed speed regressions introduced in the last few versions.
* Models should now be slightly more robust to noise in the input text, as I'm
  now training on data with a small amount of noise added, e.g. I randomly corrupt
  capitalization, swap spaces for newlines, etc. This is bringing a small
  benefit on out-of-domain data. I think this strategy could yield better
  results with a better noise-generation function. If you think you have a good
  way to make clean text resemble the kind of noisy input you're seeing in your
  domain, get in touch.

2015-06-24 v0.86
----------------

* Parser now more accurate, using novel non-monotonic transition system that's
  currently under review.


2015-05-12 v0.85
----------------

* Parser produces richer dependency labels following the `ClearNLP scheme`_
* Training data now includes text from a variety of genres.
* Parser now uses more memory and the data is slightly larger, due to the additional
  labels. Impact on efficiency is minimal: entire process still takes
  <10ms per document.

Most users should see a substantial increase in accuracy from the new model.
Long post on accuracy evaluation and model details coming soon.

.. _ClearNLP scheme: https://github.com/clir/clearnlp-guidelines/blob/master/md/dependency/dependency_guidelines.md


2015-05-12 v0.84
----------------

* Bug fixes for parsing
* Bug fixes for named entity recognition

2015-04-13 v0.80
----------------

* Preliminary support for named-entity recognition. Its accuracy is substantially behind the state-of-the-art. I'm working on improvements. 

* Better sentence boundary detection, drawn from the syntactic structure.

* Lots of bug fixes.

2015-03-05 v0.70
----------------

* Improved parse navigation API
* Bug fixes to labelled parsing


2015-01-30 spaCy v0.4: Still alpha, improving quickly
-----------------------------------------------------

Five days ago I presented the alpha release of spaCy, a natural language
processing library that brings state-of-the-art technology to small companies.

spaCy has been well received, and there are now a lot of eyes on the project.
Naturally, lots of issues have surfaced.  I'm grateful to those who've reported
them.  I've worked hard to address them as quickly as I could.

Bug Fixes
----------

* Lexemes.bin data file had a platform-specific encoding.
    This was a silly error: instead of the string, or an index into the
    list of strings, I was storing the 64-bit hash of the string.  On
    wide-unicode builds, a unicode string hashes differently.  This meant that
    all look-ups into the vocabulary failed on wide unicode builds, which
    further meant that the part-of-speech tagger and parser features were not
    computed correctly.

    The fix is simple: we already have to read in a list of all the strings, so
    just store an index into that list, instead of a hash.

* Parse tree navigation API was rough, and buggy.
    The parse-tree navigation API was the last thing I added before v0.3.  I've
    now replaced it with something better.  The previous API design was flawed,
    and the implementation was buggy --- Token.child() and Token.head were
    sometimes inconsistent.

    I've addressed the most immediate problems, but this part of the design is
    still a work in progress.  It's a difficult problem.  The parse is a tree,
    and we want to freely navigate up and down it without creating reference
    cycles that inhibit garbage collection, and without doing a lot of copying,
    creating and deleting.

    I think I've got a promising solution to this, but I suspect there's
    currently a memory leak.  Please get in touch no the tracker if you want to
    know more, especially if you think you can help.

Known Issues
------------

Some systems are still experiencing memory errors, which I'm having trouble
pinning down or reproducing.  Please send details of your system to the
`Issue Tracker`_ if this is happening to you.

.. _Issue Tracker: https://github.com/honnibal/spaCy/issues

Enhancements: Train and evaluate on whole paragraphs
----------------------------------------------------

.. note:: tl;dr: I shipped the wrong parsing model with 0.3.  That model expected input to be segmented into sentences.  0.4 ships the correct model, which uses some algorithmic tricks to minimize the impact of tokenization and sentence segmentation errors on the parser.


Most English parsing research is performed on text with perfect pre-processing:
one newline between every sentence, one space between every token.
It's always been done this way, and it's good.  It's a useful idealisation,
because the pre-processing has few algorithmic implications.

But, for practical performance, this stuff can matter a lot.
Dridan and Oepen (2013) did a simple but rare thing: they actually ran a few
parsers on raw text.  Even on the standard Wall Street Journal corpus,
where pre-processing tools are quite good, the quality of pre-processing
made a big difference:

    +-------------+-------+----------+
    | Preprocess  | BLLIP | Berkeley |
    +-------------+-------+----------+
    | Gold        | 90.9  | 89.8     |
    +-------------+-------+----------+
    | Default     | 86.4  | 88.4     |
    +-------------+-------+----------+
    | Corrected   | 89.9  | 88.8     |
    +-------------+-------+----------+

.. note:: spaCy is evaluated on unlabelled dependencies, where the above accuracy figures refer to phrase-structure trees.  Accuracies are non-comparable.



In the standard experimental condition --- gold pre-processing --- the
BLLIP parser is better.  But, it turns out it ships with lousy pre-processing
tools: when you evaluate the parsers on raw text, the BLLIP parser falls way
behind.  To verify that this was due to the quality of the pre-processing
tools, and not some particular algorithmic sensitivity, Dridan and Oepen ran
both parsers with their high-quality tokenizer and sentence segmenter.  This
confirmed that with equal pre-processing, the BLLIP parser is better.

The Dridan and Oepen paper really convinced me to take pre-processing seriously
in spaCy.  In fact, spaCy started life as just a tokenizer --- hence the name.

The spaCy parser has a special trick up its sleeve.  Because both the tagger
and parser run in linear time, it doesn't require that the input be divided
into sentences.  This is nice because it avoids error-cascades: if you segment
first, then the parser just has to live with whatever decision the segmenter
made.

But, even though I designed the system with this consideration in mind,
I decided to present the initial results using the standard methodology, using
gold-standard inputs.  But...then I made a mistake.

Unfortunately, with all the other things I was doing before launch, I forgot
all about this problem. spaCy launched with a parsing model that expected the
input to be segmented into sentences, but with no sentence segmenter.  This
caused a drop in parse accuracy of 4%!

Over the last five days, I've worked hard to correct this.  I implemented the
modifications to the parsing algorithm I had planned, from Dongdong Zhang et al.
(2013), and trained and evaluated the parser on raw text, using the version of
the WSJ distributed by Read et al. (2012), and used in Dridan and Oepen's
experiments.

I'm pleased to say that on the WSJ at least, spaCy 0.4 performs almost exactly
as well on raw text as text with gold-standard tokenization and sentence
boundary detection.

I still need to evaluate this on web text, and I need to compare against the
Stanford CoreNLP and other parsers.  I suspect that most other parsers will
decline in accuracy by 1% --- we'll see.


+-------------+---------+
| Preprocess  | spaCy   |
+-------------+---------+
| Gold        | 92.4%   |
+-------------+---------+
| Default     | 92.2%   |
+-------------+---------+

2015-01-25
----------

spaCy v0.33 launched --- first alpha build.

Updates
=======

2015-01-30 spaCy v0.4: Still alpha, improving quickly
-----------------------------------------------------

Five days ago I presented the alpha release of spaCy, a natural language
processing library that brings state-of-the-art technology to small companies.

spaCy has been very well received, and there are now a lot of eyes on the project.
Naturally, lots of issues have surfaced.  I'm very grateful to those who've reported
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
    The parse-tree navigation API was the last thing I added before v0.3. I've
    now replaced it with something better.  The previous API design was flawed,
    and the implementation was buggy --- Token.child() and Token.head were
    sometimes inconsistent.

    I've addressed the most immediate problems, but this part of the design is
    still a work in progress. It's a difficult problem. The parse is a tree,
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

.. note:: tl;dr: I shipped the wrong parsing model with 0.3. That model expected input to be segmented into sentences.  0.4 ships the correct model, which uses some algorithmic tricks to minimize the impact of tokenization and sentence segmentation errors on the parser.


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

.. note:: spaCy is evaluated on unlabelled dependencies, where the above accuracy figures refer to phrase-structure trees. Accuracies are non-comparable.



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
modifications to the parsing algorithm I had planned, from Dongdong Zhang et al
(2013), and trained and evaluated the parser on raw text, using the version of
the WSJ distributed by Read et al (2012), and used in Dridan and Oepen's
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

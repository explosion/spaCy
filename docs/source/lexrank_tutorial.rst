===================================
Tutorial: Extractive Summarization
===================================

This tutorial will go through the implementation of several extractive
summarization models with spaCy.

An *extractive* summarization system is a filter over the original document/s:
most of the text is removed, and the remaining text is formatted as a summary.
In contrast, an *abstractive* summarization system generates new text.

Application Context
-------------------

Extractive summarization systems need an application context.  We can't ask how
to design the system without some concept of what sort of summary will be
useful for a given application.  (Contrast with speech recognition, where
a notion of "correct" is much less application-sensitive.)

For this, I've adopted the application context that `Flipboard`_ discuss in a
recent blog post: they want to display lead-text to readers on mobile devices,
so that readers can easily choose interesting links.

I've chosen this application context for two reasons.  First, `Flipboard`_ say
they're putting something like this into production.  Second, there's a ready
source of evaluation data.  We can look at the lead-text that human editors
have chosen, and evaluate whether our automatic system chooses similar text.

Experimental Setup
------------------

Instead of scraping data, I'm using articles from the New York Times Annotated
Corpus, which is a handy dump of XML-annotated articles distributed by the LDC.
The annotations come with a field named "online lead paragraph".  Our
summarization systems will be evaluated on their Rouge-1 overlap with this
field.

Further details of the experimental setup can be found in the appendices.

.. _newyorktimes.com: http://newyorktimes.com

.. _Flipboard: http://engineering.flipboard.com/2014/10/summarization/

.. _vector-space model: https://en.wikipedia.org/wiki/Vector_space_model

.. _LexRank algorithm: https://www.cs.cmu.edu/afs/cs/project/jair/pub/volume22/erkan04a-html/erkan04a.html

.. _PageRank: https://en.wikipedia.org/wiki/PageRank

Summarizer API
--------------

Each summarization model will have the following API:

.. py:func:`summarize(nlp: spacy.en.English, headline: unicode, paragraphs: List[unicode],
                      target_length: int) --> summary: unicode

We receive the headline and a list of paragraphs, and a target length.  We have
to produce a block of text where len(text) < target_length.  We want summaries
that users will click-on, and not bounce back out of.  Long-term, we want
summaries that would keep people using the app.

Baselines: Truncate
-------------------

.. code:: python

    def truncate_chars(nlp, headline, paragraphs, target_length):
        text = ' '.join(paragraphs)
        return text[:target_length - 3] + '...'

    def truncate_words(nlp, headline, paragraphs, target_length):
        text = ' '.join(paragraphs)
        tokens = text.split()
        summary = []
        n_words = 0
        n_chars = 0
        while n_chars < target_length - 3:
            n_chars += len(tokens[n_words])
            n_chars += 1 # Space
            n_words += 1
        return ' '.join(tokens[:n_words]) + '...'

    def truncate_sentences(nlp, headline, paragraphs, target_length):
        sentences = []
        summary = ''
        for para in paragraphs:
            tokens = nlp(para)
            for sentence in tokens.sentences():
                if len(summary) + len(sentence) >= target_length:
                    return summary
                summary += str(sentence)
        return summary

I'd be surprised if Flipboard never had something like this in production.  Details
like lead-text take a while to float up the priority list.  This strategy also has
the advantage of transparency: it's obvious to users how the decision is being
made, so nobody is likely to complain about the feature if it works this way.

Instead of cutting off the text mid-word, we can tokenize the text, and 

+----------------+-----------+
| System         | Rouge-1 R |
+----------------+-----------+
| Truncate chars | 69.3      |
+----------------+-----------+
| Truncate words | 69.8      |
+----------------+-----------+
| Truncate sents | 48.5      |
+----------------+-----------+

Sentence Vectors
----------------

A simple bag-of-words model can be created using the `count_by` method, which
produces a dictionary of frequencies, keyed by string IDs:

.. code:: python
    
    >>> from spacy.en import English
    >>> from spacy.en.attrs import SIC
    >>> nlp = English()
    >>> tokens = nlp(u'a a a. b b b b.')
    >>> tokens.count_by(SIC)
    {41L: 4, 11L: 3, 5L: 2}
    >>> [s.count_by(SIC) for s in tokens.sentences()]
    [{11L: 3, 5L: 1}, {41L: 4, 5L: 1}]


Similar functionality is provided by `scikit-learn`_, but with a different
style of API design.  With spaCy, functions generally have more limited
responsibility.  The advantage of this is that spaCy's APIs are much simpler,
and it's often easier to compose functions in a more flexible way.

One particularly powerful feature of spaCy is its support for
`word embeddings`_ --- the dense vectors introduced by deep learning models, and
now commonly produced by `word2vec`_ and related systems.

Once a set of word embeddings has been installed, the vectors are available
from any token:

    >>> from spacy.en import English
    >>> from spacy.en.attrs import SIC
    >>> from scipy.spatial.distance import cosine
    >>> nlp = English()
    >>> tokens = nlp(u'Apple banana Batman hero')
    >>> cosine(tokens[0].vec, tokens[1].vec)



    

.. _word embeddings: https://colah.github.io/posts/2014-07-NLP-RNNs-Representations/

.. _word2vec: https://code.google.com/p/word2vec/

.. code:: python

    def main(db_loc, output_dir, feat_type="tfidf"):
        nlp = spacy.en.English()

        # Read stop list and make TF-IDF weights --- data needed for the
        # feature extraction.
        with open(stops_loc) as file_:
            stop_words = set(nlp.vocab.strings[word.strip()] for word in file_)
        idf_weights = get_idf_weights(nlp, iter_docs(db_loc))
        if feat_type == 'tfidf':
            feature_extractor = tfidf_extractor(stop_words, idf_weights)
        elif feat_type == 'vec':
            feature_extractor = vec_extractor(stop_words, idf_weights)

        for i, text in enumerate(iter_docs(db_loc)):
            tokens = nlp(body)
            sentences = tokens.sentences()
            summary = summarize(sentences, feature_extractor)
            write_output(summary, output_dir, i)




.. _scikit-learn: http://scikit-learn.org/stable/modules/classes.html#module-sklearn.feature_extraction.text





The LexRank Algorithm
----------------------

LexRank is described as a graph-based algorithm, derived from `Google's PageRank`_.
The nodes are sentences, and the edges are the similarities between one
sentence and another.  The "graph" is fully-connected, and its edges are
undirected --- so, it's natural to represent this as a matrix:

.. code:: python

    from scipy.spatial.distance import cosine
    import numpy
    
    
    def lexrank(sent_vectors):
        n = len(sent_vectors)
        # Build the cosine similarity matrix
        matrix = numpy.ndarray(shape=(n, n))
        for i in range(n):
            for j in range(n):
                matrix[i, j] = cosine(sent_vectors[i], sent_vectors[j])
        # Normalize 
        for i in range(n):
            matrix[i] /= sum(matrix[i])
        return _pagerank(matrix)

The rows are normalized (i.e. rows sum to 1), allowing the PageRank algorithm
to be applied.  Unfortunately the PageRank implementation is rather opaque ---
it's easier to just read the Wikipedia page:

.. code:: python

    def _pagerank(matrix, d=0.85):
        # This is admittedly opaque --- just read the Wikipedia page.
        n = len(matrix)
        rank = numpy.ones(shape=(n,)) / n
        new_rank = numpy.zeros(shape=(n,))
        while not _has_converged(rank, new_rank):
            rank, new_rank = new_rank, rank
            for i in range(n):
                new_rank[i] = ((1.0 - d) / n) + (d * sum(rank * matrix[i]))
        return rank

    def _has_converged(x, y, epsilon=0.0001):
        return all(abs(x[i] - y[i]) < epsilon for i in range(n))


Initial Processing
------------------




Feature Extraction
------------------

  .. code:: python
      def sentence_vectors(sentence, idf_weights):
          tf_idf = {}
          for term, freq in sent.count_by(LEMMA).items():
              tf_idf[term] = freq * idf_weights[term]
           vectors.append(tf_idf)
           return vectors

The LexRank paper models each sentence as a bag-of-words

This is simple and fairly standard, but often gives
underwhelming results.  My idea is to instead calculate vectors from
`word-embeddings`_, which have been one of the exciting outcomes of the recent
work on deep-learning.  I had a quick look at the literature, and found
a `recent workshop paper`_ that suggested the idea was plausible.




Taking the feature representation and similarity function as parameters, the
LexRank function looks like this:


Given a list of N sentences, a function that maps a sentence to a feature
vector, and a function that computes a similarity measure of two feature
vectors, this produces a vector of N floats, which indicate how well each
sentence represents the document as a whole.

.. _Rouge: https://en.wikipedia.org/wiki/ROUGE_%28metric%29


.. _word embeddings: https://colah.github.io/posts/2014-07-NLP-RNNs-Representations/

.. _recent workshop paper: https://www.aclweb.org/anthology/W/W14/W14-1504.pdf


Document Model
--------------




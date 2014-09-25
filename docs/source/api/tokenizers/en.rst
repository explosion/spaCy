spacy.en.EN
============

.. automodule:: spacy.en

Tokenizer API
-------------

.. automethod:: spacy.en.EN.tokenize
    :noindex:

.. automethod:: spacy.en.EN.lookup
    :noindex:

Lexeme Features Flag IDs
------------------------

A number of boolean features are computed for English Lexemes. To access a feature,
pass its ID to the :py:meth:`spacy.word.Lexeme.check_flag` function.

Orthographic Features
---------------------

These features describe the `orthographic` (lettering) type of the word. The
function used to compute the value is listed along with the flag.

.. data:: IS_ALPHA

    :py:func:`spacy.orth.is_alpha`

.. data:: IS_DIGIT
    
    :py:func:`spacy.orth.is_digit`
    
.. data:: IS_UPPER

    :py:func:`spacy.orth.is_upper`

.. data:: IS_PUNCT

    :py:func:`spacy.orth.is_punct`

.. data:: IS_SPACE

    :py:func:`spacy.orth.is_space`

.. data:: IS_ASCII

    :py:func:`spacy.orth.is_ascii`

.. data:: IS_TITLE

    :py:func:`spacy.orth.is_title`

.. data:: IS_LOWER

    :py:func:`spacy.orth.is_lower`

.. data:: IS_UPPER

    :py:func:`spacy.orth.is_upper`

Distributional Orthographic Features
------------------------------------

These features describe how often the lower-cased form of the word appears
in various case-styles in a large sample of English text. See :py:func:`spacy.orth.oft_case`

.. data:: OFT_UPPER
.. data:: OFT_LOWER
.. data:: OFT_TITLE


Tag Dictionary Features
-----------------------

These features describe whether the word commonly occurs with a given
part-of-speech, in a large text corpus, using a part-of-speech tagger designed
to reduce the tag-dictionary bias of its training corpus. See
:py:func:`spacy.orth.can_tag`.

.. data:: CAN_PUNCT
.. data:: CAN_CONJ
.. data:: CAN_NUM
.. data:: CAN_DET
.. data:: CAN_ADP
.. data:: CAN_ADJ
.. data:: CAN_ADV
.. data:: CAN_VERB
.. data:: CAN_NOUN
.. data:: CAN_PDT
.. data:: CAN_POS
.. data:: CAN_PRON
.. data:: CAN_PRT

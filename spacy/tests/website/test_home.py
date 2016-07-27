from __future__ import unicode_literals
import pytest
import spacy
import os


try:
    xrange
except NameError:
    xrange = range


@pytest.fixture()
def token(doc):
    return doc[0]


@pytest.mark.models
def test_load_resources_and_process_text():
    from spacy.en import English
    nlp = English()
    doc = nlp(u'Hello, world. Here are two sentences.')


@pytest.mark.models
def test_get_tokens_and_sentences(doc):
    token = doc[0]
    sentence = next(doc.sents)
    assert token is sentence[0]
    assert sentence.text == 'Hello, world.'


@pytest.mark.models
def test_use_integer_ids_for_any_strings(nlp, token):
    hello_id = nlp.vocab.strings['Hello']
    hello_str = nlp.vocab.strings[hello_id]

    assert token.orth  == hello_id  == 3125
    assert token.orth_ == hello_str == 'Hello'


def test_get_and_set_string_views_and_flags(nlp, token):
    assert token.shape_ == 'Xxxxx'
    for lexeme in nlp.vocab:
        if lexeme.is_alpha:
            lexeme.shape_ = 'W'
        elif lexeme.is_digit:
            lexeme.shape_ = 'D'
        elif lexeme.is_punct:
            lexeme.shape_ = 'P'
        else:
            lexeme.shape_ = 'M'
    assert token.shape_ == 'W'


def test_export_to_numpy_arrays(nlp, doc):
    from spacy.attrs import ORTH, LIKE_URL, IS_OOV

    attr_ids = [ORTH, LIKE_URL, IS_OOV]
    doc_array = doc.to_array(attr_ids)
    assert doc_array.shape == (len(doc), len(attr_ids))
    assert doc[0].orth == doc_array[0, 0]
    assert doc[1].orth == doc_array[1, 0]
    assert doc[0].like_url == doc_array[0, 1]
    assert list(doc_array[:, 1]) == [t.like_url for t in doc]


@pytest.mark.models
def test_word_vectors(nlp):
    doc = nlp("Apples and oranges are similar. Boots and hippos aren't.")

    apples = doc[0]
    oranges = doc[2]
    boots = doc[6]
    hippos = doc[8]

    assert apples.similarity(oranges) > boots.similarity(hippos)


@pytest.mark.models
def test_part_of_speech_tags(nlp):
    from spacy.parts_of_speech import ADV

    def is_adverb(token):
        return token.pos == spacy.parts_of_speech.ADV

    # These are data-specific, so no constants are provided. You have to look
    # up the IDs from the StringStore.
    NNS = nlp.vocab.strings['NNS']
    NNPS = nlp.vocab.strings['NNPS']
    def is_plural_noun(token):
        return token.tag == NNS or token.tag == NNPS

    def print_coarse_pos(token):
        print(token.pos_)

    def print_fine_pos(token):
        print(token.tag_)


@pytest.mark.models
def test_syntactic_dependencies():
    def dependency_labels_to_root(token):
        '''Walk up the syntactic tree, collecting the arc labels.'''
        dep_labels = []
        while token.head is not token:
            dep_labels.append(token.dep)
            token = token.head
        return dep_labels


@pytest.mark.models
def test_named_entities():
    def iter_products(docs):
        for doc in docs:
            for ent in doc.ents:
                if ent.label_ == 'PRODUCT':
                    yield ent

    def word_is_in_entity(word):
        return word.ent_type != 0

    def count_parent_verb_by_person(docs):
        counts = defaultdict(defaultdict(int))
        for doc in docs:
            for ent in doc.ents:
                if ent.label_ == 'PERSON' and ent.root.head.pos == VERB:
                    counts[ent.orth_][ent.root.head.lemma_] += 1
        return counts


def test_calculate_inline_mark_up_on_original_string():
    def put_spans_around_tokens(doc, get_classes):
        '''Given some function to compute class names, put each token in a
        span element, with the appropriate classes computed.

        All whitespace is preserved, outside of the spans. (Yes, I know HTML
        won't display it. But the point is no information is lost, so you can
        calculate what you need, e.g. <br /> tags, <p> tags, etc.)
        '''
        output = []
        template = '<span classes="{classes}">{word}</span>{space}'
        for token in doc:
            if token.is_space:
                output.append(token.orth_)
            else:
                output.append(
                  template.format(
                    classes=' '.join(get_classes(token)),
                    word=token.orth_,
                    space=token.whitespace_))
        string = ''.join(output)
        string = string.replace('\n', '')
        string = string.replace('\t', '    ')
        return string


@pytest.mark.models
def test_efficient_binary_serialization(doc):
    from spacy.tokens.doc import Doc

    byte_string = doc.to_bytes()
    open('moby_dick.bin', 'wb').write(byte_string)

    nlp = spacy.en.English()
    for byte_string in Doc.read_bytes(open('moby_dick.bin', 'rb')):
       doc = Doc(nlp.vocab)
       doc.from_bytes(byte_string)


@pytest.mark.models
def test_multithreading(nlp):
    texts = [u'One document.', u'...', u'Lots of documents']
    # .pipe streams input, and produces streaming output
    iter_texts = (texts[i % 3] for i in xrange(100000000))
    for i, doc in enumerate(nlp.pipe(iter_texts, batch_size=50, n_threads=4)):
        assert doc.is_parsed
        if i == 100:
            break


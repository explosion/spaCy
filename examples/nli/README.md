# A Decomposable Attention Model for Natural Language Inference

This directory contains an implementation of entailment prediction model described
by Parikh et al. (2016). The model is notable for its competitive performance
with very few parameters.

https://arxiv.org/pdf/1606.01933.pdf

The model is implemented using Keras and spaCy. Keras is used to build and
train the network, while spaCy is used to load the GloVe vectors, perform the
feature extraction, and help you apply the model at run-time. The following
demo code shows how the entailment model can be used at runtime, once the hook is
installed to customise the `.similarity()` method of spaCy's `Doc` and `Span`
objects:

    def demo(model_dir):
        nlp = spacy.load('en', path=model_dir,
                create_pipeline=create_similarity_pipeline)
        doc1 = nlp(u'Worst fries ever! Greasy and horrible...')
        doc2 = nlp(u'The milkshakes are good. The fries are bad.')
        print(doc1.similarity(doc2))
        sent1a, sent1b = doc1.sents
        print(sent1a.similarity(sent1b))
        print(sent1a.similarity(doc2))
        print(sent1b.similarity(doc2))

I'm working on a blog post to explain Parikh et al.'s model in more detail.
I think it is a very interesting example of the attention mechanism, which
I didn't understand very well before working through this paper.

# How to run the example

1. Install spaCy and its English models (about 1GB of data):

    pip install spacy
    python -m spacy.en.download

This will give you the spaCy's tokenization, tagging, NER and parsing models,
as well as the GloVe word vectors.

2. Install Keras

    pip install keras

3. Get Keras working with your GPU

You're mostly on your own here. My only advice is, if you're setting up on AWS,
try using the AMI published by NVidia. With the image, getting everything set
up wasn't *too* painful. 

4. Test the Keras model:

    py.test nli/keras_decomposable_attention.py

This should tell you that two tests passed.

5. Download the Stanford Natural Language Inference data

http://nlp.stanford.edu/projects/snli/

6. Train the model:

    python nli/ train <your_model_dir> <train_directory> <dev_directory>

Training takes about 300 epochs for full accuracy, and I haven't rerun the full
experiment since refactoring things to publish this example --- please let me
know if I've broken something.

You should get to at least 85% on the development data.

7. Evaluate the model (optional):

    python nli/ evaluate <your_model_dir> <dev_directory>

8. Run the demo (optional):

    python nli/ demo <your_model_dir>

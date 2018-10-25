<a href="https://explosion.ai"><img src="https://explosion.ai/assets/img/logo.svg" width="125" height="125" align="right" /></a>

# A decomposable attention model for Natural Language Inference
**by Matthew Honnibal, [@honnibal](https://github.com/honnibal)**
**Updated for spaCy 2.0+ and Keras 2.2.2+ by John Stewart, [@free-variation](https://github.com/free-variation)**

This directory contains an implementation of the entailment prediction model described
by [Parikh et al. (2016)](https://arxiv.org/pdf/1606.01933.pdf). The model is notable
for its competitive performance with very few parameters.

The model is implemented using [Keras](https://keras.io/) and [spaCy](https://spacy.io).
Keras is used to build and train the network. spaCy is used to load
the [GloVe](http://nlp.stanford.edu/projects/glove/) vectors, perform the
feature extraction, and help you apply the model at run-time. The following
demo code shows how the entailment model  can be used at runtime, once the
hook is installed to customise the `.similarity()` method of spaCy's `Doc`
and `Span` objects:

```python
def demo(shape):
	nlp = spacy.load('en_vectors_web_lg')
    nlp.add_pipe(KerasSimilarityShim.load(nlp.path / 'similarity', nlp, shape[0]))

    doc1 = nlp(u'The king of France is bald.')
    doc2 = nlp(u'France has no king.')

    print("Sentence 1:", doc1)
    print("Sentence 2:", doc2)

    entailment_type, confidence = doc1.similarity(doc2)
    print("Entailment type:", entailment_type, "(Confidence:", confidence, ")")
```

Which gives the output `Entailment type: contradiction (Confidence: 0.60604566)`, showing that
the system has definite opinions about Betrand Russell's [famous conundrum](https://users.drew.edu/jlenz/br-on-denoting.html)!

I'm working on a blog post to explain Parikh et al.'s model in more detail.
A [notebook](https://github.com/free-variation/spaCy/blob/master/examples/notebooks/Decompositional%20Attention.ipynb) is available that briefly explains this implementation.
I think it is a very interesting example of the attention mechanism, which
I didn't understand very well before working through this paper. There are
lots of ways to extend the model.

## What's where

| File | Description |
| --- | --- |
| `__main__.py` | The script that will be executed. Defines the CLI, the data reading, etc — all the boring stuff. |
| `spacy_hook.py` | Provides a class `KerasSimilarityShim` that lets you use an arbitrary function to customize spaCy's `doc.similarity()` method. Instead of the default average-of-vectors algorithm, when you call `doc1.similarity(doc2)`, you'll get the result of `your_model(doc1, doc2)`. |
| `keras_decomposable_attention.py` | Defines the neural network model. |

## Setting up

First, install [Keras](https://keras.io/), [spaCy](https://spacy.io) and the spaCy
English models (about 1GB of data):

```bash
pip install keras
pip install spacy
python -m spacy download en_vectors_web_lg
```

You'll also want to get Keras working on your GPU, and you will need a backend, such as TensorFlow or Theano.
This will depend on your set up, so you're mostly on your own for this step. If you're using AWS, try the
[NVidia AMI](https://aws.amazon.com/marketplace/pp/B00FYCDDTE). It made things pretty easy.

Once you've installed the dependencies, you can run a small preliminary test of
the Keras model:

```bash
py.test keras_parikh_entailment/keras_decomposable_attention.py
```

This compiles the model and fits it with some dummy data. You should see that
both tests passed.

Finally, download the [Stanford Natural Language Inference corpus](http://nlp.stanford.edu/projects/snli/).

## Running the example

You can run the `keras_parikh_entailment/` directory as a script, which executes the file
[`keras_parikh_entailment/__main__.py`](__main__.py).  If you run the script without arguments
the usage is shown.  Running it with `-h` explains the command line arguments.

The first thing you'll want to do is train the model:

```bash
python keras_parikh_entailment/ train -t <path to SNLI train JSON> -s <path to SNLI dev JSON>
```

Training takes about 300 epochs for full accuracy, and I haven't rerun the full
experiment since refactoring things to publish this example — please let me
know if I've broken something. You should get to at least 85% on the development data even after 10-15 epochs.

The other two modes demonstrate run-time usage. I never like relying on the accuracy printed
by `.fit()` methods. I never really feel confident until I've run a new process that loads
the model and starts making predictions, without access to the gold labels. I've therefore
included an `evaluate` mode. 

```bash
python keras_parikh_entailment/ evaluate -s <path to SNLI train JSON>
```

Finally, there's also a little demo, which mostly exists to show
you how run-time usage will eventually look.

```bash
python keras_parikh_entailment/ demo
```

## Getting updates

We should have the blog post explaining the model ready before the end of the week. To get
notified when it's published, you can either follow me on [Twitter](https://twitter.com/honnibal)
or subscribe to our [mailing list](http://eepurl.com/ckUpQ5).

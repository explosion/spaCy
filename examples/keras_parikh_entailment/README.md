<a href="https://explosion.ai"><img src="https://explosion.ai/assets/img/logo.svg" width="125" height="125" align="right" /></a>

# A decomposable attention model for Natural Language Inference
**by Matthew Honnibal, [@honnibal](https://github.com/honnibal)**

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
```

I'm working on a blog post to explain Parikh et al.'s model in more detail.
I think it is a very interesting example of the attention mechanism, which
I didn't understand very well before working through this paper. There are
lots of ways to extend the model.

## What's where

| File | Description |
| --- | --- |
| `__main__.py` | The script that will be executed. Defines the CLI, the data reading, etc — all the boring stuff. |                          
| `spacy_hook.py` | Provides a class `SimilarityShim` that lets you use an arbitrary function to customize spaCy's `doc.similarity()` method. Instead of the default average-of-vectors algorithm, when you call `doc1.similarity(doc2)`, you'll get the result of `your_model(doc1, doc2)`. |
| `keras_decomposable_attention.py` | Defines the neural network model. |

## Setting up

First, install [Keras](https://keras.io/), [spaCy](https://spacy.io) and the spaCy 
English models (about 1GB of data):

```bash
pip install https://github.com/fchollet/keras/archive/master.zip
pip install spacy
python -m spacy.en.download
```

⚠️ **Important:** In order for the example to run, you'll need to install Keras from 
the master branch (and not via `pip install keras`). For more info on this, see 
[#727](https://github.com/explosion/spaCy/issues/727).

You'll also want to get Keras working on your GPU. This will depend on your
set up, so you're mostly on your own for this step. If you're using AWS, try the 
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
[`keras_parikh_entailment/__main__.py`](__main__.py). The first thing you'll want to do is train the model:

```bash
python keras_parikh_entailment/ train <train_directory> <dev_directory>
```

Training takes about 300 epochs for full accuracy, and I haven't rerun the full
experiment since refactoring things to publish this example — please let me
know if I've broken something. You should get to at least 85% on the development data.

The other two modes demonstrate run-time usage. I never like relying on the accuracy printed
by `.fit()` methods. I never really feel confident until I've run a new process that loads
the model and starts making predictions, without access to the gold labels. I've therefore
included an `evaluate` mode. Finally, there's also a little demo, which mostly exists to show
you how run-time usage will eventually look.

## Getting updates

We should have the blog post explaining the model ready before the end of the week. To get
notified when it's published, you can either the follow me on [Twitter](https://twitter.com/honnibal), 
or subscribe to our [mailing list](http://eepurl.com/ckUpQ5).

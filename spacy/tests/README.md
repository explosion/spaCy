<a href="https://explosion.ai"><img src="https://explosion.ai/assets/img/logo.svg" width="125" height="125" align="right" /></a>

# spaCy tests

spaCy uses the [pytest](http://doc.pytest.org/) framework for testing. For more info on this, see the [pytest documentation](http://docs.pytest.org/en/latest/contents.html).

Tests for spaCy modules and classes live in their own directories of the same name. For example, tests for the `Tokenizer` can be found in [`/tests/tokenizer`](tokenizer). All test modules (i.e. directories) also need to be listed in spaCy's [`setup.py`](../setup.py). To be interpreted and run, all test files and test functions need to be prefixed with `test_`.


## Table of contents

1. [Running the tests](#running-the-tests)
2. [Dos and don'ts](#dos-and-donts)
3. [Parameters](#parameters)
4. [Fixtures](#fixtures)
5. [Testing models](#testing-models)
6. [Helpers and utilities](#helpers-and-utilities)
7. [Contributing to the tests](#contributing-to-the-tests)


## Running the tests

To show print statements, run the tests with `py.test -s`. To abort after the
first failure, run them with `py.test -x`.

```bash
py.test spacy                        # run basic tests
py.test spacy --models --en          # run basic and English model tests
py.test spacy --models --all         # run basic and all model tests
py.test spacy --slow                 # run basic and slow tests
py.test spacy --models --all --slow  # run all tests
```

You can also run tests in a specific file or directory, or even only one
specific test:

```bash
py.test spacy/tests/tokenizer  # run all tests in directory
py.test spacy/tests/tokenizer/test_exceptions.py # run all tests in file
py.test spacy/tests/tokenizer/test_exceptions.py::test_tokenizer_handles_emoji # run specific test
```

## Dos and don'ts

To keep the behaviour of the tests consistent and predictable, we try to follow a few basic conventions:

* **Test names** should follow a pattern of `test_[module]_[tested behaviour]`. For example: `test_tokenizer_keeps_email` or `test_spans_override_sentiment`.
* If you're testing for a bug reported in a specific issue, always create a **regression test**. Regression tests should be named `test_issue[ISSUE NUMBER]` and live in the [`regression`](regression) directory.
* Only use `@pytest.mark.xfail` for tests that **should pass, but currently fail**. To test for desired negative behaviour, use `assert not` in your test.
* Very **extensive tests** that take a long time to run should be marked with `@pytest.mark.slow`. If your slow test is testing important behaviour, consider adding an additional simpler version.
* Tests that require **loading the models** should be marked with `@pytest.mark.models`.
* Before requiring the models, always make sure there is no other way to test the particular behaviour. In a lot of cases, it's sufficient to simply create a `Doc` object manually. See the section on [helpers and utility functions](#helpers-and-utilities) for more info on this.
* **Avoid unnecessary imports.** There should never be a need to explicitly import spaCy at the top of a file, and most components are  available as [fixtures](#fixtures). You should also avoid wildcard imports (`from module import *`).
* If you're importing from spaCy, **always use relative imports**. Otherwise, you might accidentally be running the tests over a different copy of spaCy, e.g. one you have installed on your system.
* Don't forget the **unicode declarations** at the top of each file. This way, unicode strings won't have to be prefixed with `u`.
* Try to keep the tests **readable and concise**. Use clear and descriptive variable names (`doc`, `tokens` and `text` are great), keep it short and only test for one behaviour at a time.


## Parameters

If the test cases can be extracted from the test, always `parametrize` them instead of hard-coding them into the test:

```python
@pytest.mark.parametrize('text', ["google.com", "spacy.io"])
def test_tokenizer_keep_urls(tokenizer, text):
    tokens = tokenizer(text)
    assert len(tokens) == 1
```

This will run the test once for each `text` value. Even if you're only testing  one example, it's usually best to specify it as a parameter. This will later make it easier for others to quickly add additional test cases without having to modify the test.

You can also specify parameters as tuples to test with multiple values per test:

```python
@pytest.mark.parametrize('text,length', [("U.S.", 1), ("us.", 2), ("(U.S.", 2)])
```

To test for combinations of parameters, you can add several `parametrize` markers:

```python
@pytest.mark.parametrize('text', ["A test sentence", "Another sentence"])
@pytest.mark.parametrize('punct', ['.', '!', '?'])
```

This will run the test with all combinations of the two parameters `text` and `punct`. **Use this feature sparingly**, though, as it can easily cause unneccessary or undesired test bloat.


## Fixtures

Fixtures to create instances of spaCy objects and other components should only be defined once in the global [`conftest.py`](conftest.py). We avoid having per-directory conftest files, as this can easily lead to confusion.

These are the main fixtures that are currently available:

| Fixture | Description |
| --- | --- |
| `tokenizer` | Creates **all available** language tokenizers and runs the test for **each of them**. |
| `en_tokenizer`, `de_tokenizer`, ... | Creates an English, German etc. tokenizer. |
| `en_vocab`, `en_entityrecognizer`, ... | Creates an instance of the English `Vocab`, `EntityRecognizer` object etc. |
|  `EN`, `DE`, ... |  Creates a language class with a loaded model. For more info, see [Testing models](#testing-models). |
| `text_file` | Creates an instance of `StringIO` to simulate reading from and writing to files. |
| `text_file_b` | Creates an instance of `ByteIO` to simulate reading from and writing to files. |

The fixtures can be used in all tests by simply setting them as an argument, like this:

```python
def test_module_do_something(en_tokenizer):
    tokens = en_tokenizer("Some text here")
```

If all tests in a file require a specific configuration, or use the same complex example, it can be helpful to create a separate fixture. This fixture should be added at the top of each file. Make sure to use descriptive names for these fixtures and don't override any of the global fixtures listed above. **From looking at a test, it should immediately be clear which fixtures are used, and where they are coming from.**

## Testing models

Models should only be loaded and tested **if absolutely necessary** – for example, if you're specifically testing a model's performance, or if your test is related to model loading. If you only need an annotated `Doc`, you should use the `get_doc()` helper function to create it manually instead.

To specify which language models a test is related to, set the language ID as an argument of `@pytest.mark.models`. This allows you to later run the tests with `--models --en`. You can then use the `EN` [fixture](#fixtures) to get a language
class with a loaded model.

```python
@pytest.mark.models('en')
def test_english_model(EN):
    doc = EN(u'This is a test')
```

> ⚠️ **Important note:** In order to test models, they need to be installed as a packge. The [conftest.py](conftest.py) includes a list of all available models, mapped to their IDs, e.g. `en`. Unless otherwise specified, each model that's installed in your environment will be imported and tested. If you don't have a model installed, **the test will be skipped**.

Under the hood, `pytest.importorskip` is used to import a model package and skip the test if the package is not installed. The `EN` fixture for example gets all
available models for `en`, [parametrizes](#parameters) them to run the test for *each of them*, and uses `load_test_model()` to import the model and run the test, or skip it if the model is not installed.

### Testing specific models

Using the `load_test_model()` helper function, you can also write tests for specific models, or combinations of them:

```python
from .util import load_test_model

@pytest.mark.models('en')
def test_en_md_only():
    nlp = load_test_model('en_core_web_md')
    # test something specific to en_core_web_md

@pytest.mark.models('en', 'fr')
@pytest.mark.parametrize('model', ['en_core_web_md', 'fr_depvec_web_lg'])
def test_different_models(model):
    nlp = load_test_model(model)
    # test something specific to the parametrized models
```

### Known issues and future improvements

Using `importorskip` on a list of model packages is not ideal and we're looking to improve this in the future. But at the moment, it's the best way to ensure that tests are performed on specific model packages only, and that you'll always be able to run the tests, even if you don't have *all available models* installed. (If the tests made a call to `spacy.load('en')` instead, this would load whichever model you've created an `en` shortcut for. This may be one of spaCy's default models, but it could just as easily be your own custom English model.)

The current setup also doesn't provide an easy way to only run tests on specific model versions. The `minversion` keyword argument on `pytest.importorskip` can take care of this, but it currently only checks for the package's `__version__` attribute. An alternative solution would be to load a model package's meta.json and skip if the model's version does not match the one specified in the test.

## Helpers and utilities

Our new test setup comes with a few handy utility functions that can be imported from [`util.py`](util.py).


### Constructing a `Doc` object manually with `get_doc()`

Loading the models is expensive and not necessary if you're not actually testing the model performance. If all you need ia a `Doc` object with annotations like heads, POS tags or the dependency parse, you can use `get_doc()` to construct it manually.

```python
def test_doc_token_api_strings(en_tokenizer):
    text = "Give it back! He pleaded."
    pos = ['VERB', 'PRON', 'PART', 'PUNCT', 'PRON', 'VERB', 'PUNCT']
    heads = [0, -1, -2, -3, 1, 0, -1]
    deps = ['ROOT', 'dobj', 'prt', 'punct', 'nsubj', 'ROOT', 'punct']

    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], pos=pos, heads=heads, deps=deps)
    assert doc[0].text == 'Give'
    assert doc[0].lower_ == 'give'
    assert doc[0].pos_ == 'VERB'
    assert doc[0].dep_ == 'ROOT'
```

You can construct a `Doc` with the following arguments:

| Argument | Description |
| --- | --- |
| `vocab` | `Vocab` instance to use. If you're tokenizing before creating a `Doc`, make sure to use the tokenizer's vocab. Otherwise, you can also use the `en_vocab` fixture. **(required)** |
| `words` | List of words, for example `[t.text for t in tokens]`. **(required)** |
| `heads` | List of heads as integers. |
| `pos` | List of POS tags as text values. |
| `tag` | List of tag names as text values. |
| `dep` | List of dependencies as text values. |
| `ents` | List of entity tuples with `ent_id`, `label`, `start`, `end` (for example `('Stewart Lee', 'PERSON', 0, 2)`). The `label` will be looked up in `vocab.strings[label]`. |

Here's how to quickly get these values from within spaCy:

```python
doc = nlp(u'Some text here')
print([token.head.i-token.i for token in doc])
print([token.tag_ for token in doc])
print([token.pos_ for token in doc])
print([token.dep_ for token in doc])
```

**Note:** There's currently no way of setting the serializer data for the parser without loading the models. If this is relevant to your test, constructing the `Doc` via `get_doc()` won't work.

### Other utilities

| Name | Description |
| --- | --- |
| `load_test_model` | Load a model if it's installed as a package, otherwise skip test. |
| `apply_transition_sequence(parser, doc, sequence)` | Perform a series of pre-specified transitions, to put the parser in a desired state. |
| `add_vecs_to_vocab(vocab, vectors)` | Add list of vector tuples (`[("text", [1, 2, 3])]`) to given vocab. All vectors need to have the same length. |
| `get_cosine(vec1, vec2)` | Get cosine for two given vectors. |
| `assert_docs_equal(doc1, doc2)` | Compare two `Doc` objects and `assert` that they're equal. Tests for tokens, tags, dependencies and entities. |

## Contributing to the tests

There's still a long way to go to finally reach **100% test coverage** – and we'd appreciate your help! 🙌 You can open an issue on our [issue tracker](https://github.com/explosion/spaCy/issues) and label it `tests`, or make a [pull request](https://github.com/explosion/spaCy/pulls) to this repository.

📖 **For more information on contributing to spaCy in general, check out our [contribution guidelines](https://github.com/explosion/spaCy/blob/master/CONTRIBUTING.md).**

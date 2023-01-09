<a href="https://explosion.ai"><img src="https://explosion.ai/assets/img/logo.svg" width="125" height="125" align="right" /></a>

# spaCy tests

spaCy uses the [pytest](http://doc.pytest.org/) framework for testing. For more info on this, see the [pytest documentation](http://docs.pytest.org/en/latest/contents.html).

Tests for spaCy modules and classes live in their own directories of the same name. For example, tests for the `Tokenizer` can be found in [`/tests/tokenizer`](tokenizer). All test modules (i.e. directories) also need to be listed in spaCy's [`setup.py`](../setup.py). To be interpreted and run, all test files and test functions need to be prefixed with `test_`.

> ⚠️ **Important note:** As part of our new model training infrastructure, we've moved all model tests to the [`spacy-models`](https://github.com/explosion/spacy-models) repository. This allows us to test the models separately from the core library functionality.

## Table of contents

1. [Running the tests](#running-the-tests)
2. [Dos and don'ts](#dos-and-donts)
3. [Parameters](#parameters)
4. [Fixtures](#fixtures)
5. [Helpers and utilities](#helpers-and-utilities)
6. [Contributing to the tests](#contributing-to-the-tests)

## Running the tests

To show print statements, run the tests with `py.test -s`. To abort after the
first failure, run them with `py.test -x`.

```bash
py.test spacy                        # run basic tests
py.test spacy --slow                 # run basic and slow tests
```

You can also run tests in a specific file or directory, or even only one
specific test:

```bash
py.test spacy/tests/tokenizer  # run all tests in directory
py.test spacy/tests/tokenizer/test_exceptions.py # run all tests in file
py.test spacy/tests/tokenizer/test_exceptions.py::test_tokenizer_handles_emoji # run specific test
```

## Dos and don'ts

To keep the behavior of the tests consistent and predictable, we try to follow a few basic conventions:

- **Test names** should follow a pattern of `test_[module]_[tested behaviour]`. For example: `test_tokenizer_keeps_email` or `test_spans_override_sentiment`.
- If you're testing for a bug reported in a specific issue, always create a **regression test**. Regression tests should be named `test_issue[ISSUE NUMBER]` and live in the [`regression`](regression) directory.
- Only use `@pytest.mark.xfail` for tests that **should pass, but currently fail**. To test for desired negative behavior, use `assert not` in your test.
- Very **extensive tests** that take a long time to run should be marked with `@pytest.mark.slow`. If your slow test is testing important behavior, consider adding an additional simpler version.
- If tests require **loading the models**, they should be added to the [`spacy-models`](https://github.com/explosion/spacy-models) tests.
- Before requiring the models, always make sure there is no other way to test the particular behavior. In a lot of cases, it's sufficient to simply create a `Doc` object manually. See the section on [helpers and utility functions](#helpers-and-utilities) for more info on this.
- **Avoid unnecessary imports.** There should never be a need to explicitly import spaCy at the top of a file, and many components are available as [fixtures](#fixtures). You should also avoid wildcard imports (`from module import *`).
- If you're importing from spaCy, **always use absolute imports**. For example: `from spacy.language import Language`.
- Try to keep the tests **readable and concise**. Use clear and descriptive variable names (`doc`, `tokens` and `text` are great), keep it short and only test for one behavior at a time.

## Parameters

If the test cases can be extracted from the test, always `parametrize` them instead of hard-coding them into the test:

```python
@pytest.mark.parametrize('text', ["google.com", "spacy.io"])
def test_tokenizer_keep_urls(tokenizer, text):
    tokens = tokenizer(text)
    assert len(tokens) == 1
```

This will run the test once for each `text` value. Even if you're only testing one example, it's usually best to specify it as a parameter. This will later make it easier for others to quickly add additional test cases without having to modify the test.

You can also specify parameters as tuples to test with multiple values per test:

```python
@pytest.mark.parametrize('text,length', [("U.S.", 1), ("us.", 2), ("(U.S.", 2)])
```

To test for combinations of parameters, you can add several `parametrize` markers:

```python
@pytest.mark.parametrize('text', ["A test sentence", "Another sentence"])
@pytest.mark.parametrize('punct', ['.', '!', '?'])
```

This will run the test with all combinations of the two parameters `text` and `punct`. **Use this feature sparingly**, though, as it can easily cause unnecessary or undesired test bloat.

## Fixtures

Fixtures to create instances of spaCy objects and other components should only be defined once in the global [`conftest.py`](conftest.py). We avoid having per-directory conftest files, as this can easily lead to confusion.

These are the main fixtures that are currently available:

| Fixture                             | Description                                                                  |
| ----------------------------------- | ---------------------------------------------------------------------------- |
| `tokenizer`                         | Basic, language-independent tokenizer. Identical to the `xx` language class. |
| `en_tokenizer`, `de_tokenizer`, ... | Creates an English, German etc. tokenizer.                                   |
| `en_vocab`                          | Creates an instance of the English `Vocab`.                                  |

The fixtures can be used in all tests by simply setting them as an argument, like this:

```python
def test_module_do_something(en_tokenizer):
    tokens = en_tokenizer("Some text here")
```

If all tests in a file require a specific configuration, or use the same complex example, it can be helpful to create a separate fixture. This fixture should be added at the top of each file. Make sure to use descriptive names for these fixtures and don't override any of the global fixtures listed above. **From looking at a test, it should immediately be clear which fixtures are used, and where they are coming from.**

## Helpers and utilities

Our new test setup comes with a few handy utility functions that can be imported from [`util.py`](util.py).

### Constructing a `Doc` object manually

Loading the models is expensive and not necessary if you're not actually testing the model performance. If all you need is a `Doc` object with annotations like heads, POS tags or the dependency parse, you can construct it manually.

```python
def test_doc_token_api_strings(en_vocab):
    words = ["Give", "it", "back", "!", "He", "pleaded", "."]
    pos = ['VERB', 'PRON', 'PART', 'PUNCT', 'PRON', 'VERB', 'PUNCT']
    heads = [0, 0, 0, 0, 5, 5, 5]
    deps = ['ROOT', 'dobj', 'prt', 'punct', 'nsubj', 'ROOT', 'punct']

    doc = Doc(en_vocab, words=words, pos=pos, heads=heads, deps=deps)
    assert doc[0].text == 'Give'
    assert doc[0].lower_ == 'give'
    assert doc[0].pos_ == 'VERB'
    assert doc[0].dep_ == 'ROOT'
```

### Other utilities

| Name                                               | Description                                                                                                   |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `apply_transition_sequence(parser, doc, sequence)` | Perform a series of pre-specified transitions, to put the parser in a desired state.                          |
| `add_vecs_to_vocab(vocab, vectors)`                | Add list of vector tuples (`[("text", [1, 2, 3])]`) to given vocab. All vectors need to have the same length. |
| `get_cosine(vec1, vec2)`                           | Get cosine for two given vectors.                                                                             |
| `assert_docs_equal(doc1, doc2)`                    | Compare two `Doc` objects and `assert` that they're equal. Tests for tokens, tags, dependencies and entities. |

## Contributing to the tests

There's still a long way to go to finally reach **100% test coverage** – and we'd appreciate your help! 🙌 You can open an issue on our [issue tracker](https://github.com/explosion/spaCy/issues) and label it `tests`, or make a [pull request](https://github.com/explosion/spaCy/pulls) to this repository.

📖 **For more information on contributing to spaCy in general, check out our [contribution guidelines](https://github.com/explosion/spaCy/blob/master/CONTRIBUTING.md).**

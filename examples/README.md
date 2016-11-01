<a href="https://explosion.ai"><img src="https://explosion.ai/assets/img/logo.svg" width="125" height="125" align="right" /></a>

# spaCy examples

The examples are Python scripts with well-behaved command line interfaces. For a full list of spaCy tutorials and code snippets, see the [documentation](https://spacy.io/docs/usage/tutorials).

## How to run an example

For example, to run the [`nn_text_class.py`](nn_text_class.py) script, do:

```bash
$ python examples/nn_text_class.py
usage: nn_text_class.py [-h] [-d 3] [-H 300] [-i 5] [-w 40000] [-b 24]
                        [-r 0.3] [-p 1e-05] [-e 0.005]
                        data_dir
nn_text_class.py: error: too few arguments
```

You can print detailed help with the `-h` argument.

While we try to keep the examples up to date, they are not currently exercised by the test suite, as some of them require significant data downloads or take time to train. If you find that an example is no longer running, [please tell us](https://github.com/explosion/spaCy/issues)! We know there's nothing worse than trying to figure out what you're doing wrong, and it turns out your code was never the problem.

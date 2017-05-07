<a href="https://explosion.ai"><img src="https://explosion.ai/assets/img/logo.svg" width="125" height="125" align="right" /></a>

# Contribute to spaCy

Following the v1.0 release, it's time to welcome more contributors into the spaCy project and code base 🎉 This page will give you a quick overview of how things are organised and most importantly, how to get involved.

## Table of contents
1. [Issues and bug reports](#issues-and-bug-reports)
2. [Contributing to the code base](#contributing-to-the-code-base)
3. [Code conventions](#code-conventions)
4. [Adding tests](#adding-tests)
5. [Updating the website](#updating-the-website)
6. [Submitting a tutorial](#submitting-a-tutorial)
7. [Submitting a project to the showcase](#submitting-a-project-to-the-showcase)
8. [Code of conduct](#code-of-conduct)

## Issues and bug reports

First, [do a quick search](https://github.com/issues?q=+is%3Aissue+user%3Aexplosion) to see if the issue has already been reported. If so, it's often better to just leave a comment on an existing issue, rather than creating a new one.

If you're looking for help with your code, consider posting a question on [StackOverflow](http://stackoverflow.com/questions/tagged/spacy) instead. If you tag it `spacy` and `python`, more people will see it and hopefully be able to help.

When opening an issue, use a descriptive title and include your environment (operating system, Python version, spaCy version). Our [issue template](https://github.com/explosion/spaCy/issues/new) helps you remember the most important details to include. If you've discovered a bug, you can also submit a [regression test](#fixing-bugs) straight away. When you're opening an issue to report the bug, simply refer to your pull request in the issue body.

### Tips

* **Getting info about your spaCy installation and environment**: If you're using spaCy v1.7+, you can use the command line interface to print details and even format them as Markdown to copy-paste into GitHub issues: `python -m spacy info --markdown`.

* **Sharing long blocks of code or logs**: If you need to include long code, logs or tracebacks, you can wrap them in `<details>` and `</details>`. This [collapses the content](https://developer.mozilla.org/en/docs/Web/HTML/Element/details) so it only becomes visible on click, making the issue easier to read and follow.

### Issue labels

To distinguish issues that are opened by us, the maintainers, we usually add a 💫 to the title. We also use the following system to tag our issues:

| Issue label | Description |
| --- | --- |
| [`bug`](https://github.com/explosion/spaCy/labels/bug) | Bugs and behaviour differing from documentation |
| [`enhancement`](https://github.com/explosion/spaCy/labels/enhancement) | Feature requests and improvements |
| [`install`](https://github.com/explosion/spaCy/labels/install) | Installation problems |
| [`performance`](https://github.com/explosion/spaCy/labels/performance) | Accuracy, speed and memory use problems |
| [`tests`](https://github.com/explosion/spaCy/labels/tests) | Missing or incorrect [tests](spacy/tests) |
| [`docs`](https://github.com/explosion/spaCy/labels/docs), [`examples`](https://github.com/explosion/spaCy/labels/examples) | Issues related to the [documentation](https://spacy.io/docs) and [examples](spacy/examples) |
| [`models`](https://github.com/explosion/spaCy/labels/models), `language / [name]` | Issues related to the specific [models](https://github.com/explosion/spacy-models), languages and data |
| [`linux`](https://github.com/explosion/spaCy/labels/linux), [`osx`](https://github.com/explosion/spaCy/labels/osx), [`windows`](https://github.com/explosion/spaCy/labels/windows) | Issues related to the specific operating systems |
| [`pip`](https://github.com/explosion/spaCy/labels/pip), [`conda`](https://github.com/explosion/spaCy/labels/conda) | Issues related to the specific package managers |
| [`wip`](https://github.com/explosion/spaCy/labels/wip) | Work in progress |
| [`duplicate`](https://github.com/explosion/spaCy/labels/duplicate) | Duplicates, i.e. issues that have been reported before |
| [`meta`](https://github.com/explosion/spaCy/labels/meta) | Meta topics, e.g. repo organisation and issue management |
| [`help wanted`](https://github.com/explosion/spaCy/labels/help%20wanted), [`help wanted (easy)`](https://github.com/explosion/spaCy/labels/help%20wanted%20%28easy%29) | Requests for contributions |

## Contributing to the code base

You don't have to be an NLP expert or Python pro to contribute, and we're happy to help you get started. If you're new to spaCy, a good place to start is the [`help wanted (easy)`](https://github.com/explosion/spaCy/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted+%28easy%29%22) label, which we use to tag bugs and feature requests that are easy and self-contained. If you've decided to take on one of these problems and you're making good progress, don't forget to add a quick comment to the issue. You can also use the issue to ask questions, or share your work in progress.

### What belongs in spaCy?

Every library has a different inclusion philosophy — a policy of what should be shipped in the core library, and what could be provided in other packages. Our philosophy is to prefer a smaller core library. We generally ask the following questions:

* **What would this feature look like if implemented in a separate package?** Some features would be very difficult to implement externally. For instance, anything that requires a change to the `Token` class really needs to be implemented within spaCy, because there's no convenient way to make spaCy return custom `Token` objects. In contrast, a library of word alignment functions could easily live as a separate package that depended on spaCy — there's little difference between writing `import word_aligner` and `import spacy.word_aligner`.

* **Would the feature be easier to implement if it relied on "heavy" dependencies spaCy doesn't currently require?** Python has a very rich ecosystem. Libraries like Sci-Kit Learn, Scipy, Gensim, Keras etc. do lots of useful things — but we don't want to have them as dependencies. If the feature requires functionality in one of these libraries, it's probably better to break it out into a different package.

* **Is the feature orthogonal to the current spaCy functionality, or overlapping?** spaCy strongly prefers to avoid having 6 different ways of doing the same thing. As better techniques are developed, we prefer to drop support for "the old way". However, it's rare that one approach *entirely* dominates another. It's very common that there's still a use-case for the "obsolete" approach. For instance, [WordNet](https://wordnet.princeton.edu/) is still very useful — but word vectors are better for most use-cases, and the two approaches to lexical semantics do a lot of the same things. spaCy therefore only supports word vectors, and support for WordNet is currently left for other packages.

* **Do you need the feature to get basic things done?** We do want spaCy to be at least somewhat self-contained. If we keep needing some feature in our recipes, that does provide some argument for bringing it "in house".

### Developer resources

The [spaCy developer resources](https://github.com/explosion/spacy-dev-resources) repo contains useful scripts, tools and templates  for developing spaCy, adding new languages and training new models. If you've written a script that might help others, feel free to contribute it to that repository.

### Contributor agreement

If you've made a substantial contribution to spaCy, you should fill in the [spaCy contributor agreement](.github/CONTRIBUTOR_AGREEMENT.md) to ensure that your contribution can be used across the project. If you agree to be bound by the terms of the agreement, fill in the [template]((.github/CONTRIBUTOR_AGREEMENT.md)) and include it with your pull request, or sumit it separately to [`.github/contributors/`](/.github/contributors). The name of the file should be your GitHub username, with the extension `.md`. For example, the user
example_user would create the file `.github/contributors/example_user.md`.


### Fixing bugs

When fixing a bug, first create an [issue](https://github.com/explosion/spaCy/issues) if one does not already exist. The description text can be very short – we don't want to make this too bureaucratic.

Next, create a test file named `test_issue[ISSUE NUMBER].py` in the [`spacy/tests/regression`](spacy/tests/regression) folder. Test for the bug you're fixing, and make sure the test fails. Next, add and commit your test file referencing the issue number in the commit message. Finally, fix the bug, make sure your test passes and reference the issue in your commit message.

📖 **For more information on how to add tests, check out the [tests README](spacy/tests/README.md).**

## Code conventions

Code should loosely follow [pep8](https://www.python.org/dev/peps/pep-0008/). Regular line length is **80 characters**, with some tolerance for lines up to 90 characters if the alternative would be worse — for instance, if your list comprehension comes to 82 characters, it's better not to split it over two lines.

### Python conventions

All Python code must be written in an **intersection of Python 2 and Python 3**. This is easy in Cython, but somewhat ugly in Python. Logic that deals with Python or platform compatibility should only live in [`spacy.compat`](spacy/compat.py). To distinguish them from the builtin functions, replacement functions are suffixed with an undersocre, for example `unicode_`. If you need to access the user's version or platform information, for example to show more specific error messages, you can use the `is_config()` helper function.

```python
from .compat import unicode_, json_dumps, is_config

compatible_unicode = unicode_('hello world')
compatible_json = json_dumps({'key': 'value'})
if is_config(windows=True, python2=True):
    print("You are using Python 2 on Windows.")
```

Code that interacts with the file-system should accept objects that follow the `pathlib.Path` API, without assuming that the object inherits from `pathlib.Path`. If the function is user-facing and takes a path as an argument, it should check whether the path is provided as a string. Strings should be converted to `pathlib.Path` objects.

At the time of writing (v1.7), spaCy's serialization and deserialization functions are inconsistent about accepting paths vs accepting file-like objects. The correct answer is "file-like objects" — that's what we want going forward, as it makes the library io-agnostic. Working on buffers makes the code more general, easier to test, and compatible with Python 3's asynchronous IO.

Although spaCy uses a lot of classes, inheritance is viewed with some suspicion — it's seen as a mechanism of last resort. You should discuss plans to extend the class hierarchy before implementing.

We have a number of conventions around variable naming that are still being documented, and aren't 100% strict. A general policy is that instances of the class `Doc` should by default be called `doc`, `Token` `token`, `Lexeme` `lex`, `Vocab` `vocab` and `Language` `nlp`. You should avoid naming variables that are of other types these names. For instance, don't name a text string `doc` — you should usually call this `text`. Two general code style preferences further help with naming. First, lean away from introducing temporary variables, as these clutter your namespace. This is one reason why comprehension expressions are often preferred. Second, keep your functions shortish, so that can work in a smaller scope. Of course, this is a question of trade-offs.

### Cython conventions

spaCy's core data structures are implemented as [Cython](http://cython.org/) `cdef` classes. Memory is managed through the `cymem.cymem.Pool` class, which allows you to allocate memory which will be freed when the `Pool` object is garbage collected. This means you usually don't have to worry about freeing memory. You just have to decide which Python object owns the memory, and make it own the `Pool`. When that object goes out of scope, the memory will be freed. You do have to take care that no pointers outlive the object that owns them — but this is generally quite easy.

All Cython modules should have the `# cython: infer_types=True` compiler directive at the top of the file. This makes the code much cleaner, as it avoids the need for many type declarations. If possible, you should prefer to declare your functions `nogil`, even if you don't especially care about multi-threading. The reason is that `nogil` functions help the Cython compiler reason about your code quite a lot — you're telling the compiler that no Python dynamics are possible. This lets many errors be raised, and ensures your function will run at C speed.

Cython gives you many choices of sequences: you could have a Python list, a numpy array, a memory view, a C++ vector, or a pointer. Pointers are preferred, because they are fastest, have the most explicit semantics, and let the compiler check your code more strictly. C++ vectors are also great — but you should only use them internally in functions. It's less friendly to accept a vector as an argument, because that asks the user to do much more work.

Here's how to get a pointer from a numpy array, memory view or vector:

```cython
cdef void get_pointers(np.ndarray[int, mode='c'] numpy_array, vector[int] cpp_vector, int[::1] memory_view) nogil:
    pointer1 = <int*>numpy_array.data
    pointer2 = cpp_vector.data()
    pointer3 = &memory_view[0]
```

Both C arrays and C++ vectors reassure the compiler that no Python operations are possible on your variable. This is a big advantage: it lets the Cython compiler raise many more errors for you.

When getting a pointer from a numpy array or memoryview, take care that the data is actually stored in C-contiguous order — otherwise you'll get a pointer to nonsense. The type-declarations in the code above should generate runtime errors if buffers with incorrect memory layouts are passed in.

To iterate over the array, the following style is preferred:

```cython
cdef int c_total(const int* int_array, int length) nogil:
    total = 0
    for item in int_array[:length]:
        total += item
    return total
```

If this is confusing, consider that the compiler couldn't deal with `for item in int_array:` — there's no length attached to a raw pointer, so how could we figure out where to stop? The length is provided in the slice notation as a solution to this. Note that we don't have to declare the type of `item` in the code above — the compiler can easily infer it. This gives us tidy code that looks quite like Python, but is exactly as fast as C — because we've made sure the compilation to C is trivial.

Your functions cannot be declared `nogil` if they need to create Python objects or call Python functions. This is perfectly okay — you shouldn't torture your code just to get `nogil` functions. However, if your function isn't `nogil`, you should compile your module with `cython -a --cplus my_module.pyx` and open the resulting `my_module.html` file in a browser. This will let you see how Cython is compiling your code. Calls into the Python run-time will be in bright yellow. This lets you easily see whether Cython is able to correctly type your code, or whether there are unexpected problems.

Finally, if you're new to Cython, you should expect to find the first steps a bit frustrating. It's a very large language, since it's essentially a superset of Python and C++, with additional complexity and syntax from numpy. The [documentation](http://docs.cython.org/en/latest/) isn't great, and there are many "traps for new players". Help is available on [Gitter](https://gitter.im/explosion/spaCy).

Working in Cython is very rewarding once you're over the initial learning curve. As with C and C++, the first way you write something in Cython will often be the performance-optimal approach. In contrast, Python optimisation generally requires a lot of experimentation. Is it faster to have an `if item in my_dict` check, or to use `.get()`? What about `try`/`except`? Does this numpy operation create a copy? There's no way to guess the answers to these questions, and you'll usually be dissatisfied with your results — so there's no way to know when to stop this process. In the worst case, you'll make a mess that invites the next reader to try their luck too. This is like one of those [volcanic gas-traps](http://www.wemjournal.org/article/S1080-6032%2809%2970088-2/abstract), where the rescuers keep passing out from low oxygen, causing another rescuer to follow — only to succumb themselves. In short, just say no to optimizing your Python. If it's not fast enough the first time, just switch to Cython.

### Resources to get you started

* [PEP 8 Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/) (python.org)
* [Official Cython documentation](http://docs.cython.org/en/latest/) (cython.org)
* [Writing C in Cython](https://explosion.ai/blog/writing-c-in-cython) (explosion.ai)
* [Multi-threading spaCy’s parser and named entity recogniser](https://explosion.ai/blog/multithreading-with-cython) (explosion.ai)


## Adding tests

spaCy uses the [pytest](http://doc.pytest.org/) framework for testing. For more info on this, see the [pytest documentation](http://docs.pytest.org/en/latest/contents.html). Tests for spaCy modules and classes live in their own directories of the same name. For example, tests for the `Tokenizer` can be found in [`/spacy/tests/tokenizer`](spacy/tests/tokenizer). To be interpreted and run, all test files and test functions need to be prefixed with `test_`.

When adding tests, make sure to use descriptive names, keep the code short and concise and only test for one behaviour at a time. Try to `parametrize` test cases wherever possible, use our pre-defined fixtures for spaCy components and avoid unnecessary imports.

Extensive tests that take a long time should be marked with `@pytest.mark.slow`. Tests that require the model to be loaded should be marked with `@pytest.mark.models`. Loading the models is expensive and not necessary if you're not actually testing the model performance. If all you needs ia a `Doc` object with annotations like heads, POS tags or the dependency parse, you can use the `get_doc()` utility function to construct it manually.

📖 **For more guidelines and information on how to add tests, check out the [tests README](spacy/tests/README.md).**


## Updating the website

Our [website and docs](https://spacy.io) are implemented in [Jade/Pug](https://www.jade-lang.org), and built or served by [Harp](https://harpjs.com). Jade/Pug is an extensible templating language with a readable syntax, that compiles to HTML. Here's how to view the site locally:

```bash
sudo npm install --global harp
git clone https://github.com/explosion/spaCy
cd spaCy/website
harp server
```

The docs can always use another example or more detail, and they should always be up to date and not misleading. To quickly find the correct file to edit, simply click on the "Suggest edits" button at the bottom of a page.

To make it easy to add content components, we use a [collection of custom mixins](_includes/_mixins.jade), like `+table`, `+list` or `+code`.

📖 **For more info and troubleshooting guides, check out the [website README](website).**

### Resources to get you started

* [Guide to static websites with Harp and Jade](https://ines.io/blog/the-ultimate-guide-static-websites-harp-jade) (ines.io)
* [Building a website with modular markup components (mixins)](https://explosion.ai/blog/modular-markup) (explosion.ai)
* [Jade/Pug documentation](https://pugjs.org) (pugjs.org)
* [Harp documentation](https://harpjs.com/) (harpjs.com)


## Submitting a tutorial

Did you write a [tutorial](https://spacy.io/docs/usage/tutorials) to help others use spaCy, or did you come across one that should be added to our directory? You can submit it by making a pull request to [`website/docs/usage/_data.json`](website/docs/usage/_data.json):

```json
{
    "tutorials": {
        "deep_dives": {
            "Deep Learning with custom pipelines and Keras": {
                "url": "https://explosion.ai/blog/spacy-deep-learning-keras",
                "author": "Matthew Honnibal",
                "tags": [ "keras", "sentiment" ]
            }
        }
    }
}
```

### A few tips

* A suitable tutorial should provide additional content and practical examples that are not covered as such in the docs.
* Make sure to choose the right category – `first_steps`, `deep_dives` (tutorials that take a deeper look at specific features) or `code` (programs and scripts on GitHub etc.).
* Don't go overboard with the tags. Take inspirations from the existing ones and only add tags for features (`"sentiment"`, `"pos"`) or integrations (`"jupyter"`, `"keras"`).
* Double-check the JSON markup and/or use a linter. A wrong or missing comma will (unfortunately) break the site rendering.

## Submitting a project to the showcase

Have you built a library, visualizer, demo or product with spaCy, or did you come across one that should be featured in our [showcase](https://spacy.io/docs/usage/showcase)? You can submit it by making a pull request to [`website/docs/usage/_data.json`](website/docs/usage/_data.json):

```json
{
    "showcase": {
        "visualizations": {
            "displaCy": {
                "url": "https://demos.explosion.ai/displacy",
                "author": "Ines Montani",
                "description": "An open-source NLP visualiser for the modern web",
                "image": "displacy.jpg"
            }
        }
    }
}
```

### A few tips

* A suitable third-party library should add substantial functionality, be well-documented and open-source. If it's just a code snippet or script, consider submitting it to the `code` category of the tutorials section instead.
* A suitable demo should be hosted and accessible online. Open-source code is always a plus.
* For visualizations and products, add an image that clearly shows how it looks – screenshots are ideal.
* The image should be resized to 300x188px, optimised using a tool like [ImageOptim](https://imageoptim.com/mac) and added to [`website/assets/img/showcase`](website/assets/img/showcase).
* Double-check the JSON markup and/or use a linter. A wrong or missing comma will (unfortunately) break the site rendering.

## Code of conduct

spaCy adheres to the [Contributor Covenant Code of Conduct](http://contributor-covenant.org/version/1/4/). By participating, you are expected to uphold this code.

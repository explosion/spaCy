# Code Conventions

For a general overview of code conventions for contributors, see the [section in the contributing guide](https://github.com/explosion/spaCy/blob/master/CONTRIBUTING.md#code-conventions).

1. [Code compatibility](#code-compatibility)
2. [Auto-formatting](#auto-formatting)
3. [Linting](#linting)
4. [Documenting code](#documenting-code)
5. [Type hints](#type-hints)
6. [Structuring logic](#structuring-logic)
7. [Error handling](#error-handling)

## Code compatibility

spaCy supports **Python 3.6** and above, so all code should be written compatible with 3.6. This means that there are certain new syntax features that we won't be able to use until we drop support for older Python versions. Some newer features provide backports that we can conditionally install for older versions, although we only want to do this if it's absolutely necessary.

## Auto-formatting

spaCy uses `black` for auto-formatting (which is also available as a pre-commit hook). It's recommended to configure your editor to perform this automatically, either triggered manually or whenever you save a file. We also have a GitHub action that regularly formats the code base and submits a PR if changes are available. Note that auto-formatting is currently only available for `.py` (Python) files, not for `.pyx` (Cython).

As a rule of thumb, if the auto-formatting produces output that looks messy, it can often indicate that there's a better way to structure the code to make it more concise.

```diff
- range_suggester = registry.misc.get("spacy.ngram_range_suggester.v1")(
-     min_size=1, max_size=3
- )
+ suggester_factory = registry.misc.get("spacy.ngram_range_suggester.v1")
+ range_suggester = suggester_factory(min_size=1, max_size=3)
```

In some specific cases, e.g. in the tests, it can make sense to disable auto-formatting for a specific block. You can do this by wrapping the code in `# fmt: off` and `# fmt: on`:

```diff
+ # fmt: off
text = "I look forward to using Thingamajig.  I've been told it will make my life easier..."
deps = ["nsubj", "ROOT", "advmod", "prep", "pcomp", "dobj", "punct", "",
        "nsubjpass", "aux", "auxpass", "ROOT", "nsubj", "aux", "ccomp",
        "poss", "nsubj", "ccomp", "punct"]
+ # fmt: on
```

## Linting

[`flake8`](http://flake8.pycqa.org/en/latest/) is a tool for enforcing code style. It scans one or more files and outputs errors and warnings. This feedback can help you stick to general standards and conventions, and can be very useful for spotting potential mistakes and inconsistencies in your code. Code you write should be compatible with our flake8 rules and not cause any warnings.

```bash
flake8 spacy
```

The most common problems surfaced by linting are:

- **Trailing or missing whitespace.** This is related to formatting and should be fixed automatically by running `black`.
- **Unused imports.** Those should be removed if the imports aren't actually used. If they're required, e.g. to expose them so they can be imported from the given module, you can add a comment and `# noqa: F401` exception (see details below).
- **Unused variables.** This can often indicate bugs, e.g. a variable that's declared and not correctly passed on or returned. To prevent ambiguity here, your code shouldn't contain unused variables. If you're unpacking a list of tuples and end up with variables you don't need, you can call them `_` to indicate that they're unused.
- **Redefinition of function.** This can also indicate bugs, e.g. a copy-pasted function that you forgot to rename and that now replaces the original function.
- **Repeated dictionary keys.** This either indicates a bug or unnecessary duplication.

### Ignoring linter rules for special cases

To ignore a given line, you can add a comment like `# noqa: F401`, specifying the code of the error or warning we want to ignore. It's also possible to ignore several comma-separated codes at once, e.g. `# noqa: E731,E123`. In general, you should always **specify the code(s)** you want to ignore – otherwise, you may end up missing actual problems.

```python
# The imported class isn't used in this file, but imported here, so it can be
# imported *from* here by another module.
from .submodule import SomeClass  # noqa: F401

try:
    do_something()
except:  # noqa: E722
    # This bare except is justified, for some specific reason
    do_something_else()
```

## Documenting code

All functions and methods you write should be documented with a docstring inline. The docstring can contain a simple summary, and an overview of the arguments and their (simplified) types. This information will be shown to users when they use call the function or method in their code.

If it's part of the public API and there's a documentation section available, we usually add the link as `DOCS:` at the end. This allows us to keep the docstrings simple and concise, while also providing additional information and examples if necessary.

```python
def has_pipe(self, name: str) -> bool:
    """Check if a component name is present in the pipeline. Equivalent to
    `name in nlp.pipe_names`.

    name (str): Name of the component.
    RETURNS (bool): Whether a component of the name exists in the pipeline.

    DOCS: https://spacy.io/api/language#has_pipe
    """
    ...
```

We specifically chose this approach of maintaining the docstrings and API reference separately, instead of auto-generating the API docs from the docstrings like other packages do. We want to be able to provide extensive explanations and examples in the documentation and use our own custom markup for it that would otherwise clog up the docstrings. We also want to be able to update the documentation independently of the code base. It's slightly more work, but it's absolutely worth it in terms of user and developer experience.

### Inline code comments

We don't expect you to add inline comments for everything you're doing – this should be obvious from reading the code. If it's not, the first thing to check is whether your code can be improved to make it more explicit. That said, if your code includes complex logic or aspects that may be unintuitive at first glance (or even included a subtle bug that you ended up fixing), you should leave a quick comment that provides more context.

```diff
token_index = indices[value]
+ # Index describes Token.i of last token but Span indices are inclusive
span = doc[prev_token_index:token_index + 1]
```

```diff
+ # To create the components we need to use the final interpolated config
+ # so all values are available (if component configs use variables).
+ # Later we replace the component config with the raw config again.
interpolated = filled.interpolate() if not filled.is_interpolated else filled
```

Don't be shy about including comments for tricky parts that _you_ found hard to implement or get right – those may come in handy for the next person working on this code, or even future you!

If your change implements a fix to a specific issue, it can often be helpful to include the issue number in the comment, especially if it's a relatively straightforward adjustment:

```diff
+ # Ensure object is a Span, not a Doc (#1234)
if isinstance(obj, Doc):
    obj = obj[obj.start:obj.end]
```

### Including TODOs

It's fine to include code comments that indicate future TODOs, using the `TODO:` prefix. Modern editors typically format this in a different color, so it's easy to spot. TODOs don't necessarily have to be things that are absolutely critical to fix fight now – those should already be addressed in your pull request once it's ready for review. But they can include notes about potential future improvements.

```diff
+ # TODO: this is currently pretty slow
dir_checksum = hashlib.md5()
for sub_file in sorted(fp for fp in path.rglob("*") if fp.is_file()):
    dir_checksum.update(sub_file.read_bytes())
```

If any of the TODOs you've added are important and should be fixed soon, you should add a task for this on the project board or an issue on the issue tracker to make sure we don't forget to address it.

## Type hints

We use Python type hints across the `.py` files wherever possible. This makes it easy to understand what a function expects and returns, and modern editors will be able to show this information to you when you call an annotated function. Type hints not currently used in the `.pyx` (Cython) code, except for definitions of registered functions and component factories, where they're used for config validation.

If possible, you should always use the more descriptive type hints like `List[str]` or even `List[Any]` instead of only `list`. If possible, we also try to annotate arguments and return types of `Callable` – although, you can simplify this if the type otherwise gets too verbose (e.g. functions that return factories to create callbacks).

```diff
- def func(some_arg: dict):
+ def func(some_arg: Dict[str, Any]):
    ...
```

For model architectures, Thinc also provides a collection of [custom types](https://thinc.ai/docs/api-types), including more specific types for arrays and model inputs/outputs. Even outside of static type checking, using these types will make the code a lot easier to read and follow, since it's always clear what array types are expected (and what might go wrong if the output is different from the expected type).

```python
def build_tagger_model(
    tok2vec: Model[List[Doc], List[Floats2d]], nO: Optional[int] = None
) -> Model[List[Doc], List[Floats2d]]:
    ...
```

In some cases, you won't be able to import a class from a different module to use it as a type hint because it'd cause circular imports. For instance, `spacy/util.py` includes various helper functions that return an instance of `Language`, but we couldn't import it, because `spacy/language.py` imports `util` itself. In this case, we can provide `"Language"` as a string and make the import conditional on `typing.TYPE_CHECKING` so it only runs when the code is evaluated by a type checker:

```python
from typing TYPE_CHECKING

if TYPE_CHECKING:
    from .language import Language

def load_model(name: str) -> "Language":
    ...
```

## Structuring logic

### Positional and keyword arguments

We generally try to avoid writing functions and methods with too many arguments, and use keyword-only arguments wherever possible. Python lets you define arguments as keyword-only by separating them with a `, *`. If you're writing functions with additional arguments that customize the behavior, you typically want to make those arguments keyword-only, so their names have to be provided explicitly.

```diff
- def do_something(name: str, validate: bool = False):
+ def do_something(name: str, *, validate: bool = False):
    ...

- do_something("some_name", True)
+ do_something("some_name", validate=True)
```

This makes the function calls easier to read, because it's immediately clear what the additional values mean. It also makes it easier to extend arguments or change their order later on, because you don't end up with any function calls that depend on a specific positional order.

### Don't use `try`/`except` for control flow

We strongly discourage using `try`/`except` blocks for anything that's not third-party error handling or error handling that we otherwise have little control over. There's typically always a way to anticipate the _actual_ problem and **check for it explicitly**, which makes the code easier to follow and understand, and prevents bugs:

```diff
- try:
-     token = doc[i]
- except IndexError:
-     token = doc[-1]

+ if i < len(doc):
+     token = doc[i]
+ else:
+     token = doc[-1]
```

Even if you end up having to check for multiple conditions explicitly, this is still preferred over a catch-all `try`/`except`. It can be very helpful to think about the exact scenarios you need to cover, and what could go wrong at each step, which often leads to better code and fewer bugs. `try/except` blocks can also easily mask _other_ bugs and problems that raise the same errors you're catching, which is obviously bad.

If you have to use `try`/`except`, make sure to only include what's **absolutely necessary** in the `try` block and define the exception(s) explicitly. Otherwise, you may end up masking very different exceptions caused by other bugs.

```diff
- try:
-     value1 = get_some_value()
-     value2 = get_some_other_value()
-     score = external_library.compute_some_score(value1, value2)
- except:
-     score = 0.0

+ value1 = get_some_value()
+ value2 = get_some_other_value()
+ try:
+     score = external_library.compute_some_score(value1, value2)
+ except ValueError:
+     score = 0.0
```

## Error handling

We always encourage writing helpful and detailed custom error messages for everything we can anticipate going wrong, and including as much detail as possible. spaCy provides a directory of error messages in `errors.py` with unique codes for each message. This allows us to keep the code base more concise and avoids long and nested blocks of texts throughout the code that disrupt the reading flow. The codes make it easy to find references to the same error in different places, and also helps identify problems reported by users (since we can just search for the error code).

Errors can be referenced via their code, e.g. `Errors.E123`. Messages can also include placeholders for values, that can be populated by formatting the string with `.format()`.

```python
class Errors:
    E123 = "Something went wrong"
    E456 = "Unexpected value: {value}"
```

```diff
if something_went_wrong:
-    raise ValueError("Something went wrong!")
+    raise ValueError(Errors.E123)

if not isinstance(value, int):
-    raise ValueError(f"Unexpected value: {value}")
+    raise ValueError(Errors.E456.format(value=value))
```

As a general rule of thumb, all error messages raised within the **core library** should be added to `Errors`. The only place where we write errors and messages as strings is `spacy.cli`, since these functions typically pretty-print and generate a lot of output that'd otherwise be very difficult to separate from the actual logic.

### Re-raising exceptions

If we anticipate possible errors in third-party code that we don't control, or our own code in a very different context, we typically try to provide custom and more specific error messages if possible. If we need to re-raise an exception within a `try`/`except` block, we can add re-raise a custom exception.

[Re-raising `from`](https://docs.python.org/3/tutorial/errors.html#exception-chaining) the original caught exception lets us chain the exceptions, so the user sees both the original error, as well as the custom message with a note "The above exception was the direct cause of the following exception".

```diff
try:
   run_third_party_code_that_might_fail()
except ValueError as e:
+    raise ValueError(Errors.E123) from e
```

In some cases, it makes sense to suppress the original exception, e.g. if we know what it is and know that it's not particularly helpful. In that case, we can raise `from None`. The prevents clogging up the user's terminal with multiple and irrelevant chained exceptions.

```diff
try:
   run_our_own_code_that_might_fail_confusingly()
except ValueError:
+    raise ValueError(Errors.E123) from None
```

### Avoid using naked `assert`

During development, it can sometimes be helpful to add `assert` statements throughout your code to make sure that the values you're working with are what you expect. However, as you clean up your code, those should either be removed or replaced by more explicit error handling:

```diff
- assert score >= 0.0
+ if score < 0.0:
+     raise ValueError(Errors.789.format(score=score))
```

Otherwise, the user will get to see a naked `AssertionError` with no further explanation, which is very unhelpful. Instead of adding an error message to `assert`, it's always better to `raise` more explicit errors for specific conditions. If you're checking for something that _has to be right_ and would otherwise be a bug in spaCy, you can express this in the error message:

```python
E161 = ("Found an internal inconsistency when predicting entity links. "
        "This is likely a bug in spaCy, so feel free to open an issue: "
        "https://github.com/explosion/spaCy/issues")
```

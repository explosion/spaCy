# StringStore & Vocab

## Overview

spaCy represents mosts strings internally using a `uint64` in Cython which
corresponds to a hash. The magic required to make this largely transparent is
handled by the `StringStore`, and is integrated into the pipelines using the
`Vocab`, which also connects it to some other information. 

These are mostly internal details that average library users should never have
to think about. On the other hand, when developing a component it's normal to
interact with the Vocab for lexeme data or word vectors, and it's not unusual
to add labels to the `StringStore`.

## StringStore

### Overview

The `StringStore` is a `cdef class` that looks a bit like a two-way dictionary,
though it is not a subclass of anything in particular.

The main functionality of the `StringStore` is that `__getitem__` converts
hashes into strings or strings into hashes. The details of this are very messy
but generally not a problem in practice.

Example:

```
from spacy.strings import StringStore

ss = StringStore()
hashval = ss["spacy"] # 10639093010105930009
try:
  # this won't work
  ss[hashval]
except KeyError:
  print(f"key {hashval} unknown in the StringStore.")

ss.add("spacy")
assert ss[hashval] == "spacy" # it works now

# There is no `.keys` property, but you can iterate over keys
# The empty string will never be in the list of keys
for key in ss:
  print(key)
```

Almost all strings in spaCy are stored in the `StringStore`. This naturally
includes tokens, but also includes things like labels (not just NER/POS/dep,
but also categories etc.), lemmas, lowercase forms, word shapes, and so on. One
of the main results of this is that tokens can be represented by a compact C
struct that mostly consists of string hashes. This also means that converting
input for the models is straightforward, and there's not a token mapping step
like in many machine learning frameworks. Additionally, because the token IDs
in spaCy are based on hashes, they are consistent across environments or
models.

One pattern you'll see a lot in spaCy APIs is that `something.value` returns an
`int` and `something.value_` returns a string. That's implemented using the
`StringStore`. Typically the `int` is stored in a C struct and the string is
generated via a property that calls into the `StringStore` with the `int`.

Besides `__getitem__`, the `StringStore` has functions to return specifically a
string or specifically a hash, regardless of whether the input was a string or
hash to begin with, though these are only used occasionally. (Maybe they can be
removed?)

### Implementation Details: Hashes and Allocations

Hashes are 64-bit and are computed using murmurhash on UTF-8 bytes. There is no
mechanism for detecting and avoiding collisions. To date there has never been a
reproducible collision or user report about any related issues.

The empty string is not hashed, it's just converted to/from 0. 

A small number of strings use indices into a lookup table (so low integers)
rather than hashes. This is mostly Universal Dependencies labels or other
strings considered "core" in spaCy. This was critical in v1, which hadn't
introduced hashing yet. Since v2 it's important for items in `spacy.attrs`,
especially lexeme flags, but is otherwise only maintained for backwards
compatability.

You can call `strings["mystring"]` with a string the `StringStore` has never seen
before and it will return a hash. But in order to do the reverse operation, you
need to call `strings.add("mystring")` first. Without a call to `add` the
string will not be interned.

In normal use nothing is ever removed from the `StringStore`. In theory this
means that if you do something like iterate through all hex values of a certain
length you can have explosive memory usage. In practice this has never been an
issue. (Note that this is also different from using `sys.intern` to intern
Python strings, which does not guarantee they won't be memory collected later.)

Strings are stored in the `StringStore` in a peculiar way: short strings are stored
in a fixed-length buffer (one per string, not a shared buffer), while longer
strings are prefixed with their length and use malloced memory. If you want to
understand the full details see the implementation of `decode_Utf8Str` and
`_allocate` in `strings.pyx`.

### Notes on Python & Cython String Types

The `StringStore` doesn't do anything too weird with Python strings, but because
it's in Cython some of the type details of Python strings become important.

In Python 2 strings were more like sequences of bytes, but in Python 3 they're
more like UTF-8 sequences and treated separately from bytes. Cython has several
string types to manage compatability with bytes and strings in Python 2 and 3:
`str`, `unicode`, `bytes`, and `basestring`. 

Here is how the types work in Python 3:

- `str` and `unicode` are the same
- `bytes` is just `bytes`
- `basestring` is the union of `str` and `unicode`, so in Py3 all are equivalent

`basestring` and `unicode` are still used in several places in spaCy code,
presumably as a legacy of Python 2 support. In Python 3 there should be no
difference between these types and `str`.

### When to Use the StringStore?

While you can ignore the `StringStore` in many cases, there are situations where
you should make use of it to avoid errors. 

Any time you introduce a string that may be set on a `Doc` field that has a hash,
you should add the string to the `StringStore`. This mainly happens when adding
labels in components, but there are some other cases:

- syntax iterators, mainly `get_noun_chunks`
- external data used in components, like the `KnowledgeBase` in the `entity_linker`
- labels used in tests

## Vocab

The `Vocab` is a core component of a `Language` pipeline. Its main function is
to manage `Lexeme`s, which are structs that contain information about a token
that depends only on its surface form, without context. `Lexeme`s store much of
the data associated with `Token`s. As a side effect of this the `Vocab` also
manages the `StringStore` for a pipeline and a grab-bag of other data.

These are things stored in the vocab:

- `Lexeme`s
- `StringStore`
- `Morphology`: manages info used in `MorphAnalysis` objects
- `vectors`: basically a dict for word vectors
- `lookups`: language specific data like lemmas
- `writing_system`: language specific metadata
- `get_noun_chunks`: a syntax iterator
- `data_dir`: unused?
- lex attribute getters: functions like `is_punct`, set in language defaults
- `cfg`: **not** the pipeline config, this is mostly unused

Some of these, like the Morphology and Vectors, are complex enough that they
need their own explanations. Here we'll just look at Vocab-specific items.

### Lexemes

A `Lexeme` is a type that mainly wraps a `LexemeC`, a struct consisting of ints
that identify various context-free token attributes. Lexemes are the core data
of the `Vocab`, and can be accessed using `__getitem__` on the `Vocab`. The memory
for storing `LexemeC` objects is managed by a pool that belongs to the `Vocab`.

Note that `__getitem__` on the `Vocab` works much like the `StringStore`, in
that it accepts a hash or id, with one important difference: if you do a lookup
using a string, that value is added to the `StringStore` automatically. 

The attributes stored in a `LexemeC` are:

- orth (the raw text)
- lower
- norm
- shape
- prefix
- suffix

Most of these are straightforward. All of them can be customized, and (except
`orth`) probably should be since the defaults are based on English, but in
practice this is rarely done at present.

### Lookups

This is basically a dict of dicts, implemented using a `Table` for each
sub-dict, that stores lemmas and other language-specific lookup data. 

A `Table` is a subclass of `OrderedDict` used for string-to-string data. It uses
Bloom filters to speed up misses and has some extra serialization features.
Tables are not used outside of the lookups.

### Lex Attribute Getters

Lexical Attribute Getters like `is_punct` are defined on a per-language basis,
much like lookups, but take the form of functions rather than string-to-string
dicts, so they're stored separately.

### Writing System

This is a dict with three attributes:

- `direction`: ltr or rtl (default ltr)
- `has_case`: bool (default `True`)
- `has_letters`: bool (default `True`, `False` only for CJK for now)

Currently these are not used much - the main use is that `direction` is used in
visualizers, though `rtl` doesn't quite work. In the future they could be used
when choosing hyperparameters for subwords, controlling word shape generation,
and similar tasks.

### Other Vocab Members

Some members of the Vocab have less clear purposes. The Vocab is kind of the
default place to store things from `Language.defaults` that don't belong to the
Tokenizer, which explains most of these.

- `get_noun_chunks`
- `cfg`: This is a dict that just stores `oov_prob` (hardcoded to `-20`)
- `data_dir`: This seems to be serialization related but presently unused.



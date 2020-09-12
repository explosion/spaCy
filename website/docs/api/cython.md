---
title: Cython Architecture
next: /api/cython-structs
menu:
  - ['Overview', 'overview']
  - ['Conventions', 'conventions']
---

## Overview {#overview hidden="true"}

> #### What's Cython?
>
> [Cython](http://cython.org/) is a language for writing C extensions for
> Python. Most Python code is also valid Cython, but you can add type
> declarations to get efficient memory-managed code just like C or C++.

This section documents spaCy's C-level data structures and interfaces, intended
for use from Cython. Some of the attributes are primarily for internal use, and
all C-level functions and methods are designed for speed over safety – if you
make a mistake and access an array out-of-bounds, the program may crash
abruptly.

With Cython there are four ways of declaring complex data types. Unfortunately
we use all four in different places, as they all have different utility:

| Declaration     | Description                                                                                                                                                                                                                                                                      | Example                                                                |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `class`         | A normal Python class.                                                                                                                                                                                                                                                           | [`Language`](/api/language)                                            |
| `cdef class`    | A Python extension type. Differs from a normal Python class in that its attributes can be defined on the underlying struct. Can have C-level objects as attributes (notably structs and pointers), and can have methods which have C-level objects as arguments or return types. | [`Lexeme`](/api/cython-classes#lexeme)                                 |
| `cdef struct`   | A struct is just a collection of variables, sort of like a named tuple, except the memory is contiguous. Structs can't have methods, only attributes.                                                                                                                            | [`LexemeC`](/api/cython-structs#lexemec)                               |
| `cdef cppclass` | A C++ class. Like a struct, this can be allocated on the stack, but can have methods, a constructor and a destructor. Differs from `cdef class` in that it can be created and destroyed without acquiring the Python global interpreter lock. This style is the most obscure.    | [`StateC`](%%GITHUB_SPACY/spacy/pipeline/_parser_internals/_state.pxd) |

The most important classes in spaCy are defined as `cdef class` objects. The
underlying data for these objects is usually gathered into a struct, which is
usually named `c`. For instance, the [`Lexeme`](/api/cython-classses#lexeme)
class holds a [`LexemeC`](/api/cython-structs#lexemec) struct, at `Lexeme.c`.
This lets you shed the Python container, and pass a pointer to the underlying
data into C-level functions.

## Conventions {#conventions}

spaCy's core data structures are implemented as [Cython](http://cython.org/)
`cdef` classes. Memory is managed through the
[`cymem`](https://github.com/explosion/cymem) `cymem.Pool` class, which allows
you to allocate memory which will be freed when the `Pool` object is garbage
collected. This means you usually don't have to worry about freeing memory. You
just have to decide which Python object owns the memory, and make it own the
`Pool`. When that object goes out of scope, the memory will be freed. You do
have to take care that no pointers outlive the object that owns them — but this
is generally quite easy.

All Cython modules should have the `# cython: infer_types=True` compiler
directive at the top of the file. This makes the code much cleaner, as it avoids
the need for many type declarations. If possible, you should prefer to declare
your functions `nogil`, even if you don't especially care about multi-threading.
The reason is that `nogil` functions help the Cython compiler reason about your
code quite a lot — you're telling the compiler that no Python dynamics are
possible. This lets many errors be raised, and ensures your function will run at
C speed.

Cython gives you many choices of sequences: you could have a Python list, a
numpy array, a memory view, a C++ vector, or a pointer. Pointers are preferred,
because they are fastest, have the most explicit semantics, and let the compiler
check your code more strictly. C++ vectors are also great — but you should only
use them internally in functions. It's less friendly to accept a vector as an
argument, because that asks the user to do much more work. Here's how to get a
pointer from a numpy array, memory view or vector:

```python
cdef void get_pointers(np.ndarray[int, mode='c'] numpy_array, vector[int] cpp_vector, int[::1] memory_view) nogil:
pointer1 = <int*>numpy_array.data
pointer2 = cpp_vector.data()
pointer3 = &memory_view[0]
```

Both C arrays and C++ vectors reassure the compiler that no Python operations
are possible on your variable. This is a big advantage: it lets the Cython
compiler raise many more errors for you.

When getting a pointer from a numpy array or memoryview, take care that the data
is actually stored in C-contiguous order — otherwise you'll get a pointer to
nonsense. The type-declarations in the code above should generate runtime errors
if buffers with incorrect memory layouts are passed in. To iterate over the
array, the following style is preferred:

```python
cdef int c_total(const int* int_array, int length) nogil:
    total = 0
    for item in int_array[:length]:
        total += item
    return total
```

If this is confusing, consider that the compiler couldn't deal with
`for item in int_array:` — there's no length attached to a raw pointer, so how
could we figure out where to stop? The length is provided in the slice notation
as a solution to this. Note that we don't have to declare the type of `item` in
the code above — the compiler can easily infer it. This gives us tidy code that
looks quite like Python, but is exactly as fast as C — because we've made sure
the compilation to C is trivial.

Your functions cannot be declared `nogil` if they need to create Python objects
or call Python functions. This is perfectly okay — you shouldn't torture your
code just to get `nogil` functions. However, if your function isn't `nogil`, you
should compile your module with `cython -a --cplus my_module.pyx` and open the
resulting `my_module.html` file in a browser. This will let you see how Cython
is compiling your code. Calls into the Python run-time will be in bright yellow.
This lets you easily see whether Cython is able to correctly type your code, or
whether there are unexpected problems.

Working in Cython is very rewarding once you're over the initial learning curve.
As with C and C++, the first way you write something in Cython will often be the
performance-optimal approach. In contrast, Python optimization generally
requires a lot of experimentation. Is it faster to have an `if item in my_dict`
check, or to use `.get()`? What about `try`/`except`? Does this numpy operation
create a copy? There's no way to guess the answers to these questions, and
you'll usually be dissatisfied with your results — so there's no way to know
when to stop this process. In the worst case, you'll make a mess that invites
the next reader to try their luck too. This is like one of those
[volcanic gas-traps](http://www.wemjournal.org/article/S1080-6032%2809%2970088-2/abstract),
where the rescuers keep passing out from low oxygen, causing another rescuer to
follow — only to succumb themselves. In short, just say no to optimizing your
Python. If it's not fast enough the first time, just switch to Cython.

<Infobox title="Resources" emoji="📖">

- [Official Cython documentation](http://docs.cython.org/en/latest/)
  (cython.org)
- [Writing C in Cython](https://explosion.ai/blog/writing-c-in-cython)
  (explosion.ai)
- [Multi-threading spaCy’s parser and named entity recognizer](https://explosion.ai/blog/multithreading-with-cython)
  (explosion.ai)

</Infobox>

# Language

> Reference: `spacy/language.py`

1. [Constructing the `nlp` object from a config](#1-constructing-the-nlp-object-from-a-config)
   - [A. Overview of `Language.from_config`](#1a-overview)
   - [B. Component factories](#1b-how-pipeline-component-factories-work-in-the-config)
   - [C. Sourcing a component](#1c-sourcing-a-pipeline-component)
   - [D. Tracking components as they're modified](#1d-tracking-components-as-theyre-modified)
   - [E. spaCy's config utility function](#1e-spacys-config-utility-functions)
2. [Initialization](#initialization)
   - [A. Initialization for training](#2a-initialization-for-training): `init_nlp`
   - [B. Initializing the `nlp` object](#2b-initializing-the-nlp-object): `Language.initialize`
   - [C. Initializing the vocab](#2c-initializing-the-vocab): `init_vocab`

## 1. Constructing the `nlp` object from a config

### 1A. Overview

Most of the functions referenced in the config are regular functions with arbitrary arguments registered via the function registry. However, the pipeline components are a bit special: they don't only receive arguments passed in via the config file, but also the current `nlp` object and the string `name` of the individual component instance (so a user can have multiple components created with the same factory, e.g. `ner_one` and `ner_two`). This name can then be used by the components to add to the losses and scores. This special requirement means that pipeline components can't just be resolved via the config the "normal" way: we need to retrieve the component functions manually and pass them their arguments, plus the `nlp` and `name`.

The `Language.from_config` classmethod takes care of constructing the `nlp` object from a config. It's the single place where this happens and what `spacy.load` delegates to under the hood. Its main responsibilities are:

- **Load and validate the config**, and optionally **auto-fill** all missing values that we either have defaults for in the config template or that registered function arguments define defaults for. This helps ensure backwards-compatibility, because we're able to add a new argument `foo: str = "bar"` to an existing function, without breaking configs that don't specity it.
- **Execute relevant callbacks** for pipeline creation, e.g. optional functions called before and after creation of the `nlp` object and pipeline.
- **Initialize language subclass and create tokenizer**. The `from_config` classmethod will always be called on a language subclass, e.g. `English`, not on `Language` directly. Initializing the subclass takes a callback to create the tokenizer.
- **Set up the pipeline components**. Components can either refer to a component factory or a `source`, i.e. an existing pipeline that's loaded and that the component is then copied from. We also need to ensure that we update the information about which components are disabled.
- **Manage listeners.** If sourced components "listen" to other components (`tok2vec`, `transformer`), we need to ensure that the references are valid. If the config specifies that listeners should be replaced by copies (e.g. to give the `ner` component its own `tok2vec` model instead of listening to the shared `tok2vec` component in the pipeline), we also need to take care of that.

Note that we only resolve and load **selected sections** in `Language.from_config`, i.e. only the parts that are relevant at runtime, which is `[nlp]` and `[components]`. We don't want to be resolving anything related to training or initialization, since this would mean loading and constructing unnecessary functions, including functions that require information that isn't necessarily available at runtime, like `paths.train`.

### 1B. How pipeline component factories work in the config

As opposed to regular registered functions that refer to a registry and function name (e.g. `"@misc": "foo.v1"`), pipeline components follow a different format and refer to their component `factory` name. This corresponds to the name defined via the `@Language.component` or `@Language.factory` decorator. We need this decorator to define additional meta information for the components, like their default config and score weights.

```ini
[components.my_component]
factory = "foo"
some_arg = "bar"
other_arg = ${paths.some_path}
```

This means that we need to create and resolve the `config["components"]` separately from the rest of the config. There are some important considerations and things we need to manage explicitly to avoid unexpected behavior:

#### Variable interpolation

When a config is resolved, references to variables are replaced, so that the functions receive the correct value instead of just the variable name. To interpolate a config, we need it in its entirety: we couldn't just interpolate a subsection that refers to variables defined in a different subsection. So we first interpolate the entire config.

However, the `nlp.config` should include the original config with variables intact – otherwise, loading a pipeline and saving it to disk will destroy all logic implemented via variables and hard-code the values all over the place. This means that when we create the components, we need to keep two versions of the config: the interpolated config with the "real" values and the `raw_config` including the variable references.

#### Factory registry

Component factories are special and use the `@Language.factory` or `@Language.component` decorator to register themselves and their meta. When the decorator runs, it performs some basic validation, stores the meta information for the factory on the `Language` class (default config, scores etc.) and then adds the factory function to `registry.factories`. The `component` decorator can be used for registering simple functions that just take a `Doc` object and return it so in that case, we create the factory for the user automatically.

There's one important detail to note about how factories are registered via entry points: A package that wants to expose spaCy components still needs to register them via the `@Language` decorators so we have the component meta information and can perform required checks. All we care about here is that the decorated function is **loaded and imported**. When it is, the `@Language` decorator takes care of everything, including actually registering the component factory.

Normally, adding to the registry via an entry point will just add the function to the registry under the given name. But for `spacy_factories`, we don't actually want that: all we care about is that the function decorated with `@Language` is imported so the decorator runs. So we only exploit Python's entry point system to automatically import the function, and the `spacy_factories` entry point group actually adds to a **separate registry**, `registry._factories`, under the hood. Its only purpose is that the functions are imported. The decorator then runs, creates the factory if needed and adds it to the `registry.factories` registry.

#### Language-specific factories

spaCy supports registering factories on the `Language` base class, as well as language-specific subclasses like `English` or `German`. This allows providing different factories depending on the language, e.g. a different default lemmatizer. The `Language.get_factory_name` classmethod constructs the factory name as `{lang}.{name}` if a language is available (i.e. if it's a subclass) and falls back to `{name}` otherwise. So `@German.factory("foo")` will add a factory `de.foo` under the hood. If you add `nlp.add_pipe("foo")`, we first check if there's a factory for `{nlp.lang}.foo` and if not, we fall back to checking for a factory `foo`.

#### Creating a pipeline component from a factory

`Language.add_pipe` takes care of adding a pipeline component, given its factory name, its config. If no source pipeline to copy the component from is provided, it delegates to `Language.create_pipe`, which sets up the actual component function.

- Validate the config and make sure that the factory was registered via the decorator and that we have meta for it.
- Update the component config with any defaults specified by the component's `default_config`, if available. This is done by merging the values we receive into the defaults. It ensures that you can still add a component without having to specify its _entire_ config including more complex settings like `model`. If no `model` is defined, we use the default.
- Check if we have a language-specific factory for the given `nlp.lang` and if not, fall back to the global factory.
- Construct the component config, consisting of whatever arguments were provided, plus the current `nlp` object and `name`, which are default expected arguments of all factories. We also add a reference to the `@factories` registry, so we can resolve the config via the registry, like any other config. With the added `nlp` and `name`, it should now include all expected arguments of the given function.
- Fill the config to make sure all unspecified defaults from the function arguments are added and update the `raw_config` (uninterpolated with variables intact) with that information, so the component config we store in `nlp.config` is up to date. We do this by adding the `raw_config` _into_ the filled config – otherwise, the references to variables would be overwritten.
- Resolve the config and create all functions it refers to (e.g. `model`). This gives us the actual component function that we can insert into the pipeline.

### 1C. Sourcing a pipeline component

```ini
[components.ner]
source = "en_core_web_sm"
```

spaCy also allows ["sourcing" a component](https://spacy.io/usage/processing-pipelines#sourced-components), which will copy it over from an existing pipeline. In this case, `Language.add_pipe` will delegate to `Language.create_pipe_from_source`. In order to copy a component effectively and validate it, the source pipeline first needs to be loaded. This is done in `Language.from_config`, so a source pipeline only has to be loaded once if multiple components source from it. Sourcing a component will perform the following checks and modifications:

- For each sourced pipeline component loaded in `Language.from_config`, a hash of the vectors data from the source pipeline is stored in the pipeline meta so we're able to check whether the vectors match and warn if not (since different vectors that are used as features in components can lead to degraded performance). Because the vectors are not loaded at the point when components are sourced, the check is postponed to `init_vocab` as part of `Language.initialize`.
- If the sourced pipeline component is loaded through `Language.add_pipe(source=)`, the vectors are already loaded and can be compared directly. The check compares the shape and keys first and finally falls back to comparing the actual byte representation of the vectors (which is slower).
- Ensure that the component is available in the pipeline.
- Interpolate the entire config of the source pipeline so all variables are replaced and the component's config that's copied over doesn't include references to variables that are not available in the destination config.
- Add the source `vocab.strings` to the destination's `vocab.strings` so we don't end up with unavailable strings in the final pipeline (which would also include labels used by the sourced component).

Note that there may be other incompatibilities that we're currently not checking for and that could cause a sourced component to not work in the destination pipeline. We're interested in adding more checks here but there'll always be a small number of edge cases we'll never be able to catch, including a sourced component depending on other pipeline state that's not available in the destination pipeline.

### 1D. Tracking components as they're modified

The `Language` class implements methods for removing, replacing or renaming pipeline components. Whenever we make these changes, we need to update the information stored on the `Language` object to ensure that it matches the current state of the pipeline. If a user just writes to `nlp.config` manually, we obviously can't ensure that the config matches the reality – but since we offer modification via the pipe methods, it's expected that spaCy keeps the config in sync under the hood. Otherwise, saving a modified pipeline to disk and loading it back wouldn't work. The internal attributes we need to keep in sync here are:

| Attribute                | Type                         | Description                                                                                                                                                     |
| ------------------------ | ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Language._components`   | `List[Tuple[str, Callable]]` | All pipeline components as `(name, func)` tuples. This is used as the source of truth for `Language.pipeline`, `Language.pipe_names` and `Language.components`. |
| `Language._pipe_meta`    | `Dict[str, FactoryMeta]`     | The meta information of a component's factory, keyed by component name. This can include multiple components referring to the same factory meta.                |
| `Language._pipe_configs` | `Dict[str, Config]`          | The component's config, keyed by component name.                                                                                                                |
| `Language._disabled`     | `Set[str]`                   | Names of components that are currently disabled.                                                                                                                |
| `Language._config`       | `Config`                     | The underlying config. This is only internals and will be used as the basis for constructing the config in the `Language.config` property.                      |

In addition to the actual component settings in `[components]`, the config also allows specifying component-specific arguments via the `[initialize.components]` block, which are passed to the component's `initialize` method during initialization if it's available. So we also need to keep this in sync in the underlying config.

### 1E. spaCy's config utility functions

When working with configs in spaCy, make sure to use the utility functions provided by spaCy if available, instead of calling the respective `Config` methods. The utilities take care of providing spaCy-specific error messages and ensure a consistent order of config sections by setting the `section_order` argument. This ensures that exported configs always have the same consistent format.

- `util.load_config`: load a config from a file
- `util.load_config_from_str`: load a confirm from a string representation
- `util.copy_config`: deepcopy a config

## 2. Initialization

Initialization is a separate step of the [config lifecycle](https://spacy.io/usage/training#config-lifecycle) that's not performed at runtime. It's implemented via the `training.initialize.init_nlp` helper and calls into `Language.initialize` method, which sets up the pipeline and component models before training. The `initialize` method takes a callback that returns a sample of examples, which is used to initialize the component models, add all required labels and perform shape inference if applicable.

Components can also define custom initialization setting via the `[initialize.components]` block, e.g. if they require external data like lookup tables to be loaded in. All config settings defined here will be passed to the component's `initialize` method, if it implements one. Components are expected to handle their own serialization after they're initialized so that any data or settings they require are saved with the pipeline and will be available from disk when the pipeline is loaded back at runtime.

### 2A. Initialization for training

The `init_nlp` function is called before training and returns an initialized `nlp` object that can be updated with the examples. It only needs the config and does the following:

- Load and validate the config. In order to validate certain settings like the `seed`, we also interpolate the config to get the final value (because in theory, a user could provide this via a variable).
- Set up the GPU allocation, if required.
- Create the `nlp` object from the raw, uninterpolated config, which delegates to `Language.from_config`. Since this method may modify and auto-fill the config and pipeline component settings, we then use the interpolated version of `nlp.config` going forward, to ensure that what we're training with is up to date.
- Resolve the `[training]` block of the config and perform validation, e.g. to check that the corpora are available.
- Determine the components that should be frozen (not updated during training) or resumed (sourced components from a different pipeline that should be updated from the examples and not reset and re-initialized). To resume training, we can call the `nlp.resume_training` method.
- Initialize the `nlp` object via `nlp.initialize` and pass it a `get_examples` callback that returns the training corpus (used for shape inference, setting up labels etc.). If the training corpus is streamed, we only provide a small sample of the data, which can potentially be infinite. `nlp.initialize` will delegate to the components as well and pass the data sample forward.
- Check the listeners and warn about components dependencies, e.g. if a frozen component listens to a component that is retrained, or vice versa (which can degrade results).

### 2B. Initializing the `nlp` object

The `Language.initialize` method does the following:

- **Resolve the config** defined in the `[initialize]` block separately (since everything else is already available in the loaded `nlp` object), based on the fully interpolated config.
- **Execute callbacks**, i.e. `before_init` and `after_init`, if they're defined.
- **Initialize the vocab**, including vocab data, lookup tables and vectors.
- **Initialize the tokenizer** if it implements an `initialize` method. This is not the case for the default tokenizers, but it allows custom tokenizers to depend on external data resources that are loaded in on initialization.
- **Initialize all pipeline components** if they implement an `initialize` method and pass them the `get_examples` callback, the current `nlp` object as well as well additional initialization config settings provided in the component-specific block.
- **Initialize pretraining** if a `[pretraining]` block is available in the config. This allows loading pretrained tok2vec weights in `spacy pretrain`.
- **Register listeners** if token-to-vector embedding layers of a component model "listen" to a previous component (`tok2vec`, `transformer`) in the pipeline.
- **Create an optimizer** on the `Language` class, either by adding the optimizer passed as `sgd` to `initialize`, or by creating the optimizer defined in the config's training settings.

### 2C. Initializing the vocab

Vocab initialization is handled in the `training.initialize.init_vocab` helper. It takes the relevant loaded functions and values from the config and takes care of the following:

- Add lookup tables defined in the config initialization, e.g. custom lemmatization tables. Those will be added to `nlp.vocab.lookups` from where they can be accessed by components.
- Add JSONL-formatted [vocabulary data](https://spacy.io/api/data-formats#vocab-jsonl) to pre-populate the lexical attributes.
- Load vectors into the pipeline. Vectors are defined as a name or path to a saved `nlp` object containing the vectors, e.g. `en_vectors_web_lg`. It's loaded and the vectors are ported over, while ensuring that all source strings are available in the destination strings. We also warn if there's a mismatch between sourced vectors, since this can lead to problems.

# spaCy Satellite Packages

This is a list of all the active repos relevant to spaCy besides the main one, with short descriptions, history, and current status. Archived repos will not be covered.

## Always Included in spaCy

These packages are always pulled in when you install spaCy. Most of them are direct dependencies, but some are transitive dependencies through other packages.

- [spacy-legacy](https://github.com/explosion/spacy-legacy): When an architecture in spaCy changes enough to get a new version, the old version is frozen and moved to spacy-legacy. This allows us to keep the core library slim while also preserving backwards compatability.
- [thinc](https://github.com/explosion/thinc): Thinc is the machine learning library that powers trainable components in spaCy. It wraps backends like Numpy, PyTorch, and Tensorflow to provide a functional interface for specifying architectures.
- [catalogue](https://github.com/explosion/catalogue): Small library for adding function registries, like those used for model architectures in spaCy.
- [confection](https://github.com/explosion/confection): This library contains the functionality for config parsing that was formerly contained directly in Thinc.
- [spacy-loggers](https://github.com/explosion/spacy-loggers): Contains loggers beyond the default logger available in spaCy&#39;s core code base. This includes loggers integrated with third-party services, which may differ in release cadence from spaCy itself.
- [wasabi](https://github.com/explosion/wasabi): A command line formatting library, used for terminal output in spaCy.
- [srsly](https://github.com/explosion/srsly): A wrapper that vendors several serialization libraries for spaCy. Includes parsers for JSON, JSONL, MessagePack, (extended) Pickle, and YAML.
- [preshed](https://github.com/explosion/preshed): A Cython library for low-level data structures like hash maps, used for memory efficient data storage.
- [cython-blis](https://github.com/explosion/cython-blis): Fast matrix multiplication using BLIS without depending on system libraries. Required by Thinc, rather than spaCy directly.
- [murmurhash](https://github.com/explosion/murmurhash): A wrapper library for a C++ murmurhash implementation, used for string IDs in spaCy and preshed.
- [cymem](https://github.com/explosion/cymem): A small library for RAII-style memory management in Cython. 

## Optional Extensions for spaCy

These are repos that can be used by spaCy but aren&#39;t part of a default installation. Many of these are wrappers to integrate various kinds of third-party libraries.

- [spacy-transformers](https://github.com/explosion/spacy-transformers): A wrapper for the [HuggingFace Transformers](https://huggingface.co/docs/transformers/index) library, this handles the extensive conversion necessary to coordinate spaCy&#39;s powerful `Doc` representation, training pipeline, and the Transformer embeddings. When released, this was known as `spacy-pytorch-transformers`, but it changed to the current name when HuggingFace update the name of their library as well.
- [spacy-huggingface-hub](https://github.com/explosion/spacy-huggingface-hub): This package has a CLI script for uploading a packaged spaCy pipeline (created with `spacy package`) to the [Hugging Face Hub](https://huggingface.co/models).
- [spacy-alignments](https://github.com/explosion/spacy-alignments): A wrapper for the tokenizations library (mentioned below) with a modified build system to simplify cross-platform wheel creation. Used in spacy-transformers for aligning spaCy and HuggingFace tokenizations.
- [spacy-experimental](https://github.com/explosion/spacy-experimental): Experimental components that are not quite ready for inclusion in the main spaCy library. Usually there are unresolved questions around their APIs, so the experimental library allows us to expose them to the community for feedback before fully integrating them. 
- [spacy-lookups-data](https://github.com/explosion/spacy-lookups-data): A repository of linguistic data, such as lemmas, that takes up a lot of disk space. Originally created to reduce the size of the spaCy core library. This is mainly useful if you want the data included but aren&#39;t using a pretrained pipeline; for the affected languages, the relevant data is included in pretrained pipelines directly.
- [coreferee](https://github.com/explosion/coreferee): Coreference resolution for English, French, German and Polish, optimised for limited training data and easily extensible for further languages. Used as a spaCy pipeline component.
- [spacy-stanza](https://github.com/explosion/spacy-stanza): This is a wrapper that allows the use of Stanford&#39;s Stanza library in spaCy. 
- [spacy-streamlit](https://github.com/explosion/spacy-streamlit): A wrapper for the Streamlit dashboard building library to help with integrating [displaCy](https://spacy.io/api/top-level/#displacy).
- [spacymoji](https://github.com/explosion/spacymoji): A library to add extra support for emoji to spaCy, such as including character names.
- [thinc-apple-ops](https://github.com/explosion/thinc-apple-ops): A special backend for OSX that uses Apple&#39;s native libraries for improved performance.
- [os-signpost](https://github.com/explosion/os-signpost): A Python package that allows you to use the `OSSignposter` API in OSX for performance analysis.
- [spacy-ray](https://github.com/explosion/spacy-ray): A wrapper to integrate spaCy with Ray, a distributed training framework. Currently a work in progress.

## Prodigy

[Prodigy](https://prodi.gy) is Explosion&#39;s easy to use and highly customizable tool for annotating data. Prodigy itself requires a license, but the repos below contain documentation, examples, and editor or notebook integrations.

- [prodigy-recipes](https://github.com/explosion/prodigy-recipes): Sample recipes for Prodigy, along with notebooks and other examples of usage.
- [vscode-prodigy](https://github.com/explosion/vscode-prodigy): A VS Code extension that lets you run Prodigy inside VS Code.
- [jupyterlab-prodigy](https://github.com/explosion/jupyterlab-prodigy): An extension for JupyterLab that lets you run Prodigy inside JupyterLab.

## Independent Tools or Projects

These are tools that may be related to or use spaCy, but are functional independent projects in their own right as well.

- [floret](https://github.com/explosion/floret): A modification of fastText to use Bloom Embeddings. Can be used to add vectors with subword features to spaCy, and also works independently in the same manner as fastText.
- [sense2vec](https://github.com/explosion/sense2vec): A library to make embeddings of noun phrases or words coupled with their part of speech. This library uses spaCy.
- [spacy-vectors-builder](https://github.com/explosion/spacy-vectors-builder): This is a spaCy project that builds vectors using floret and a lot of input text. It handles downloading the input data as well as the actual building of vectors.
- [holmes-extractor](https://github.com/explosion/holmes-extractor): Information extraction from English and German texts based on predicate logic. Uses spaCy.
- [healthsea](https://github.com/explosion/healthsea): Healthsea is a project to extract information from comments about health supplements. Structurally, it&#39;s a self-contained, large spaCy project.
- [spacy-pkuseg](https://github.com/explosion/spacy-pkuseg): A fork of the pkuseg Chinese tokenizer. Used for Chinese support in spaCy, but also works independently.
- [ml-datasets](https://github.com/explosion/ml-datasets): This repo includes loaders for several standard machine learning datasets, like MNIST or WikiNER, and has historically been used in spaCy example code and documentation.

## Documentation and Informational Repos

These repos are used to support the spaCy docs or otherwise present information about spaCy or other Explosion projects.

- [projects](https://github.com/explosion/projects): The projects repo is used to show detailed examples of spaCy usage. Individual projects can be checked out using the spaCy command line tool, rather than checking out the projects repo directly.
- [spacy-course](https://github.com/explosion/spacy-course): Home to the interactive spaCy course for learning about how to use the library and some basic NLP principles.
- [spacy-io-binder](https://github.com/explosion/spacy-io-binder): Home to the notebooks used for interactive examples in the documentation.

## Organizational / Meta

These repos are used for organizing data around spaCy, but are not something an end user would need to install as part of using the library.

- [spacy-models](https://github.com/explosion/spacy-models): This repo contains metadata (but not training data) for all the spaCy models. This includes information about where their training data came from, version compatability, and performance information. It also includes tests for the model packages, and the built models are hosted as releases of this repo.
- [wheelwright](https://github.com/explosion/wheelwright): A tool for automating our PyPI builds and releases.
- [ec2buildwheel](https://github.com/explosion/ec2buildwheel): A small project that allows you to build Python packages in the manner of cibuildwheel, but on any EC2 image. Used by wheelwright.

## Other

Repos that don&#39;t fit in any of the above categories.

- [blis](https://github.com/explosion/blis): A fork of the official BLIS library. The main branch is not updated, but work continues in various branches. This is used for cython-blis.
- [tokenizations](https://github.com/explosion/tokenizations): A library originally by Yohei Tamura to align strings with tolerance to some variations in features like case and diacritics, used for aligning tokens and wordpieces. Adopted and maintained by Explosion, but usually spacy-alignments is used instead.
- [conll-2012](https://github.com/explosion/conll-2012): A repo to hold some slightly cleaned up versions of the official scripts for the CoNLL 2012 shared task involving coreference resolution. Used in the coref project.
- [fastapi-explosion-extras](https://github.com/explosion/fastapi-explosion-extras): Some small tweaks to FastAPI used at Explosion.


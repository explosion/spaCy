# coding: utf8
from __future__ import print_function
# NB! This breaks in plac on Python 2!!
#from __future__ import unicode_literals

import plac
from spacy.cli import download as cli_download
from spacy.cli import link as cli_link
from spacy.cli import info as cli_info
from spacy.cli import package as cli_package
from spacy.cli import train as cli_train
from spacy.cli import model as cli_model
from spacy.cli import convert as cli_convert


class CLI(object):
    """Command-line interface for spaCy"""

    commands = ('download', 'link', 'info', 'package', 'train', 'model', 'convert')

    @plac.annotations(
        model=("model to download (shortcut or model name)", "positional", None, str),
        direct=("force direct download. Needs model name with version and won't "
                "perform compatibility check", "flag", "d", bool)
    )
    def download(self, model=None, direct=False):
        """
        Download compatible model from default download path using pip. Model
        can be shortcut, model name or, if --direct flag is set, full model name
        with version.
        """

        cli_download(model, direct)


    @plac.annotations(
        origin=("package name or local path to model", "positional", None, str),
        link_name=("name of shortuct link to create", "positional", None, str),
        force=("force overwriting of existing link", "flag", "f", bool)
    )
    def link(self, origin, link_name, force=False):
        """
        Create a symlink for models within the spacy/data directory. Accepts
        either the name of a pip package, or the local path to the model data
        directory. Linking models allows loading them via spacy.load(link_name).
        """

        cli_link(origin, link_name, force)


    @plac.annotations(
        model=("optional: shortcut link of model", "positional", None, str),
        markdown=("generate Markdown for GitHub issues", "flag", "md", str)
    )
    def info(self, model=None, markdown=False):
        """
        Print info about spaCy installation. If a model shortcut link is
        speficied as an argument, print model information. Flag --markdown
        prints details in Markdown for easy copy-pasting to GitHub issues.
        """

        cli_info(model, markdown)


    @plac.annotations(
        input_dir=("directory with model data", "positional", None, str),
        output_dir=("output parent directory", "positional", None, str),
        force=("force overwriting of existing folder in output directory", "flag", "f", bool)
    )
    def package(self, input_dir, output_dir, force=False):
        """
        Generate Python package for model data, including meta and required
        installation files. A new directory will be created in the specified
        output directory, and model data will be copied over.
        """

        cli_package(input_dir, output_dir, force)


    @plac.annotations(
        lang=("model language", "positional", None, str),
        output_dir=("output directory to store model in", "positional", None, str),
        train_data=("location of JSON-formatted training data", "positional", None, str),
        dev_data=("location of JSON-formatted development data (optional)", "positional", None, str),
        n_iter=("number of iterations", "option", "n", int),
        parser_L1=("L1 regularization penalty for parser", "option", "L", float),
        no_tagger=("Don't train tagger", "flag", "T", bool),
        no_parser=("Don't train parser", "flag", "P", bool),
        no_ner=("Don't train NER", "flag", "N", bool)
    )
    def train(self, lang, output_dir, train_data, dev_data=None, n_iter=15,
              parser_L1=0.0, no_tagger=False, no_parser=False, no_ner=False):
        """
        Train a model. Expects data in spaCy's JSON format.
        """

        cli_train(lang, output_dir, train_data, dev_data, n_iter, not no_tagger,
                  not no_parser, not no_ner, parser_L1)

    @plac.annotations(
        lang=("model language", "positional", None, str),
        model_dir=("output directory to store model in", "positional", None, str),
        freqs_data=("tab-separated frequencies file", "positional", None, str),
        clusters_data=("Brown clusters file", "positional", None, str),
        vectors_data=("word vectors file", "positional", None, str)
    )
    def model(self, lang, model_dir, freqs_data, clusters_data=None, vectors_data=None):
        """
        Initialize a new model and its data directory.
        """

        cli_model(lang, model_dir, freqs_data, clusters_data, vectors_data)

    @plac.annotations(
        input_file=("input file", "positional", None, str),
        output_dir=("output directory for converted file", "positional", None, str),
        n_sents=("Number of sentences per doc", "option", "n", float),
        morphology=("Enable appending morphology to tags", "flag", "m", bool)
    )
    def convert(self, input_file, output_dir, n_sents=10, morphology=False):
        """
        Convert files into JSON format for use with train command and other
        experiment management functions.
        """

        cli_convert(input_file, output_dir, n_sents, morphology)


    def __missing__(self, name):
        print("\n   Command %r does not exist."
              "\n   Use the --help flag for a list of available commands.\n" % name)


if __name__ == '__main__':
    import plac
    import sys
    sys.argv[0] = 'spacy'
    plac.Interpreter.call(CLI)

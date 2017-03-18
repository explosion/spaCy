# coding: utf8
# 
from __future__ import print_function
# NB! This breaks in plac on Python 2!!
#from __future__ import unicode_literals,

import plac
from spacy.cli import download as cli_download
from spacy.cli import link as cli_link
from spacy.cli import info as cli_info


class CLI(object):
    """Command-line interface for spaCy"""

    commands = ('download', 'link', 'info')

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
        link_name=("Name of shortuct link to create", "positional", None, str),
        force=("Force overwriting of existing link", "flag", "f", bool)
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


    def __missing__(self, name):
        print("\n   Command %r does not exist\n" % name)


if __name__ == '__main__':
    import plac
    import sys
    cli = CLI()
    sys.argv[0] = 'spacy'
    plac.Interpreter.call(CLI)

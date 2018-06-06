# coding: utf8
from __future__ import unicode_literals


class Messages(object):
    M001 = ("Download successful but linking failed")
    M002 = ("Creating a shortcut link for 'en' didn't work (maybe you "
            "don't have admin permissions?), but you can still load the "
            "model via its full package name: nlp = spacy.load('{name}')")
    M003 = ("Server error ({code})")
    M004 = ("Couldn't fetch {desc}. Please find a model for your spaCy "
            "installation (v{version}), and download it manually. For more "
            "details, see the documentation: https://spacy.io/usage/models")
    M005 = ("Compatibility error")
    M006 = ("No compatible models found for v{version} of spaCy.")
    M007 = ("No compatible model found for '{name}' (spaCy v{version}).")
    M008 = ("Can't locate model data")
    M009 = ("The data should be located in {path}")
    M010 = ("Can't find the spaCy data path to create model symlink")
    M011 = ("Make sure a directory `/data` exists within your spaCy "
            "installation and try again. The data directory should be "
            "located here:")
    M012 = ("Link '{name}' already exists")
    M013 = ("To overwrite an existing link, use the --force flag.")
    M014 = ("Can't overwrite symlink '{name}'")
    M015 = ("This can happen if your data directory contains a directory or "
            "file of the same name.")
    M016 = ("Error: Couldn't link model to '{name}'")
    M017 = ("Creating a symlink in spacy/data failed. Make sure you have the "
            "required permissions and try re-running the command as admin, or "
            "use a virtualenv. You can still import the model as a module and "
            "call its load() method, or create the symlink manually.")
    M018 = ("Linking successful")
    M019 = ("You can now load the model via spacy.load('{name}')")
    M020 = ("Can't find model meta.json")
    M021 = ("Couldn't fetch compatibility table.")
    M022 = ("Can't find spaCy v{version} in compatibility table")
    M023 = ("Installed models (spaCy v{version})")
    M024 = ("No models found in your current environment.")
    M025 = ("Use the following commands to update the model packages:")
    M026 = ("The following models are not available for spaCy "
            "v{version}: {models}")
    M027 = ("You may also want to overwrite the incompatible links using the "
            "`python -m spacy link` command with `--force`, or remove them "
            "from the data directory. Data path: {path}")
    M028 = ("Input file not found")
    M029 = ("Output directory not found")
    M030 = ("Unknown format")
    M031 = ("Can't find converter for {converter}")
    M032 = ("Generated output file {name}")
    M033 = ("Created {n_docs} documents")
    M034 = ("Evaluation data not found")
    M035 = ("Visualization output directory not found")
    M036 = ("Generated {n} parses as HTML")
    M037 = ("Can't find words frequencies file")
    M038 = ("Sucessfully compiled vocab")
    M039 = ("{entries} entries, {vectors} vectors")
    M040 = ("Output directory not found")
    M041 = ("Loaded meta.json from file")
    M042 = ("Successfully created package '{name}'")
    M043 = ("To build the package, run `python setup.py sdist` in this "
            "directory.")
    M044 = ("Package directory already exists")
    M045 = ("Please delete the directory and try again, or use the `--force` "
            "flag to overwrite existing directories.")
    M046 = ("Generating meta.json")
    M047 = ("Enter the package settings for your model. The following "
            "information will be read from your model data: pipeline, vectors.")
    M048 = ("No '{key}' setting found in meta.json")
    M049 = ("This setting is required to build your package.")
    M050 = ("Training data not found")
    M051 = ("Development data not found")
    M052 = ("Not a valid meta.json format")
    M053 = ("Expected dict but got: {meta_type}")

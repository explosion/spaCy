from typing import Optional, Union, Any, Dict
import shutil
from pathlib import Path
from wasabi import Printer, get_raw_input
import srsly
import sys

from ._util import app, Arg, Opt
from ..schemas import validate, ModelMetaSchema
from .. import util
from .. import about


@app.command("package")
def package_cli(
    # fmt: off
    input_dir: Path = Arg(..., help="Directory with pipeline data", exists=True, file_okay=False),
    output_dir: Path = Arg(..., help="Output parent directory", exists=True, file_okay=False),
    meta_path: Optional[Path] = Opt(None, "--meta-path", "--meta", "-m", help="Path to meta.json", exists=True, dir_okay=False),
    create_meta: bool = Opt(False, "--create-meta", "-c", "-C", help="Create meta.json, even if one exists"),
    name: Optional[str] = Opt(None, "--name", "-n", help="Package name to override meta"),
    version: Optional[str] = Opt(None, "--version", "-v", help="Package version to override meta"),
    no_sdist: bool = Opt(False, "--no-sdist", "-NS", help="Don't build .tar.gz sdist, can be set if you want to run this step manually"),
    force: bool = Opt(False, "--force", "-f", "-F", help="Force overwriting existing data in output directory"),
    # fmt: on
):
    """
    Generate an installable Python package for a pipeline. Includes binary data,
    meta and required installation files. A new directory will be created in the
    specified output directory, and the data will be copied over. If
    --create-meta is set and a meta.json already exists in the output directory,
    the existing values will be used as the defaults in the command-line prompt.
    After packaging, "python setup.py sdist" is run in the package directory,
    which will create a .tar.gz archive that can be installed via "pip install".

    DOCS: https://nightly.spacy.io/api/cli#package
    """
    package(
        input_dir,
        output_dir,
        meta_path=meta_path,
        name=name,
        version=version,
        create_meta=create_meta,
        create_sdist=not no_sdist,
        force=force,
        silent=False,
    )


def package(
    input_dir: Path,
    output_dir: Path,
    meta_path: Optional[Path] = None,
    name: Optional[str] = None,
    version: Optional[str] = None,
    create_meta: bool = False,
    create_sdist: bool = True,
    force: bool = False,
    silent: bool = True,
) -> None:
    msg = Printer(no_print=silent, pretty=not silent)
    input_path = util.ensure_path(input_dir)
    output_path = util.ensure_path(output_dir)
    meta_path = util.ensure_path(meta_path)
    if not input_path or not input_path.exists():
        msg.fail("Can't locate pipeline data", input_path, exits=1)
    if not output_path or not output_path.exists():
        msg.fail("Output directory not found", output_path, exits=1)
    if meta_path and not meta_path.exists():
        msg.fail("Can't find pipeline meta.json", meta_path, exits=1)
    meta_path = meta_path or input_dir / "meta.json"
    if not meta_path.exists() or not meta_path.is_file():
        msg.fail("Can't load pipeline meta.json", meta_path, exits=1)
    meta = srsly.read_json(meta_path)
    meta = get_meta(input_dir, meta)
    if name is not None:
        meta["name"] = name
    if version is not None:
        meta["version"] = version
    if not create_meta:  # only print if user doesn't want to overwrite
        msg.good("Loaded meta.json from file", meta_path)
    else:
        meta = generate_meta(meta, msg)
    errors = validate(ModelMetaSchema, meta)
    if errors:
        msg.fail("Invalid pipeline meta.json")
        print("\n".join(errors))
        sys.exit(1)
    model_name = meta["lang"] + "_" + meta["name"]
    model_name_v = model_name + "-" + meta["version"]
    main_path = output_dir / model_name_v
    package_path = main_path / model_name
    if package_path.exists():
        if force:
            shutil.rmtree(str(package_path))
        else:
            msg.fail(
                "Package directory already exists",
                "Please delete the directory and try again, or use the "
                "`--force` flag to overwrite existing directories.",
                exits=1,
            )
    Path.mkdir(package_path, parents=True)
    shutil.copytree(str(input_dir), str(package_path / model_name_v))
    create_file(main_path / "meta.json", srsly.json_dumps(meta, indent=2))
    create_file(main_path / "setup.py", TEMPLATE_SETUP)
    create_file(main_path / "MANIFEST.in", TEMPLATE_MANIFEST)
    create_file(package_path / "__init__.py", TEMPLATE_INIT)
    msg.good(f"Successfully created package '{model_name_v}'", main_path)
    if create_sdist:
        with util.working_dir(main_path):
            util.run_command([sys.executable, "setup.py", "sdist"], capture=False)
        zip_file = main_path / "dist" / f"{model_name_v}.tar.gz"
        msg.good(f"Successfully created zipped Python package", zip_file)


def create_file(file_path: Path, contents: str) -> None:
    file_path.touch()
    file_path.open("w", encoding="utf-8").write(contents)


def get_meta(
    model_path: Union[str, Path], existing_meta: Dict[str, Any]
) -> Dict[str, Any]:
    meta = {
        "lang": "en",
        "name": "pipeline",
        "version": "0.0.0",
        "description": "",
        "author": "",
        "email": "",
        "url": "",
        "license": "MIT",
    }
    meta.update(existing_meta)
    nlp = util.load_model_from_path(Path(model_path))
    meta["spacy_version"] = util.get_model_version_range(about.__version__)
    meta["vectors"] = {
        "width": nlp.vocab.vectors_length,
        "vectors": len(nlp.vocab.vectors),
        "keys": nlp.vocab.vectors.n_keys,
        "name": nlp.vocab.vectors.name,
    }
    if about.__title__ != "spacy":
        meta["parent_package"] = about.__title__
    return meta


def generate_meta(existing_meta: Dict[str, Any], msg: Printer) -> Dict[str, Any]:
    meta = existing_meta or {}
    settings = [
        ("lang", "Pipeline language", meta.get("lang", "en")),
        ("name", "Pipeline name", meta.get("name", "pipeline")),
        ("version", "Package version", meta.get("version", "0.0.0")),
        ("description", "Package description", meta.get("description", None)),
        ("author", "Author", meta.get("author", None)),
        ("email", "Author email", meta.get("email", None)),
        ("url", "Author website", meta.get("url", None)),
        ("license", "License", meta.get("license", "MIT")),
    ]
    msg.divider("Generating meta.json")
    msg.text(
        "Enter the package settings for your pipeline. The following information "
        "will be read from your pipeline data: pipeline, vectors."
    )
    for setting, desc, default in settings:
        response = get_raw_input(desc, default)
        meta[setting] = default if response == "" and default else response
    return meta


TEMPLATE_SETUP = """
#!/usr/bin/env python
import io
import json
from os import path, walk
from shutil import copy
from setuptools import setup


def load_meta(fp):
    with io.open(fp, encoding='utf8') as f:
        return json.load(f)


def list_files(data_dir):
    output = []
    for root, _, filenames in walk(data_dir):
        for filename in filenames:
            if not filename.startswith('.'):
                output.append(path.join(root, filename))
    output = [path.relpath(p, path.dirname(data_dir)) for p in output]
    output.append('meta.json')
    return output


def list_requirements(meta):
    parent_package = meta.get('parent_package', 'spacy')
    requirements = [parent_package + meta['spacy_version']]
    if 'setup_requires' in meta:
        requirements += meta['setup_requires']
    if 'requirements' in meta:
        requirements += meta['requirements']
    return requirements


def setup_package():
    root = path.abspath(path.dirname(__file__))
    meta_path = path.join(root, 'meta.json')
    meta = load_meta(meta_path)
    model_name = str(meta['lang'] + '_' + meta['name'])
    model_dir = path.join(model_name, model_name + '-' + meta['version'])

    copy(meta_path, path.join(model_name))
    copy(meta_path, model_dir)

    setup(
        name=model_name,
        description=meta.get('description'),
        author=meta.get('author'),
        author_email=meta.get('email'),
        url=meta.get('url'),
        version=meta['version'],
        license=meta.get('license'),
        packages=[model_name],
        package_data={model_name: list_files(model_dir)},
        install_requires=list_requirements(meta),
        zip_safe=False,
        entry_points={'spacy_models': ['{m} = {m}'.format(m=model_name)]}
    )


if __name__ == '__main__':
    setup_package()
""".strip()


TEMPLATE_MANIFEST = """
include meta.json
include config.cfg
""".strip()


TEMPLATE_INIT = """
from pathlib import Path
from spacy.util import load_model_from_init_py, get_model_meta


__version__ = get_model_meta(Path(__file__).parent)['version']


def load(**overrides):
    return load_model_from_init_py(__file__, **overrides)
""".strip()

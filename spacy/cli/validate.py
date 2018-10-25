# coding: utf8
from __future__ import unicode_literals, print_function

import pkg_resources
from pathlib import Path
import sys
import ujson
import requests

from ._messages import Messages
from ..compat import path2str, locale_escape
from ..util import prints, get_data_path, read_json
from .. import about


def validate():
    """Validate that the currently installed version of spaCy is compatible
    with the installed models. Should be run after `pip install -U spacy`.
    """
    r = requests.get(about.__compatibility__)
    if r.status_code != 200:
        prints(Messages.M021, title=Messages.M003.format(code=r.status_code),
               exits=1)
    compat = r.json()['spacy']
    current_compat = compat.get(about.__version__)
    if not current_compat:
        prints(about.__compatibility__, exits=1,
               title=Messages.M022.format(version=about.__version__))
    all_models = set()
    for spacy_v, models in dict(compat).items():
        all_models.update(models.keys())
        for model, model_vs in models.items():
            compat[spacy_v][model] = [reformat_version(v) for v in model_vs]
    model_links = get_model_links(current_compat)
    model_pkgs = get_model_pkgs(current_compat, all_models)
    incompat_links = {l for l, d in model_links.items() if not d['compat']}
    incompat_models = {d['name'] for _, d in model_pkgs.items()
                       if not d['compat']}
    incompat_models.update([d['name'] for _, d in model_links.items()
                            if not d['compat']])
    na_models = [m for m in incompat_models if m not in current_compat]
    update_models = [m for m in incompat_models if m in current_compat]

    prints(path2str(Path(__file__).parent.parent),
           title=Messages.M023.format(version=about.__version__))
    if model_links or model_pkgs:
        print(get_row('TYPE', 'NAME', 'MODEL', 'VERSION', ''))
        for name, data in model_pkgs.items():
            print(get_model_row(current_compat, name, data, 'package'))
        for name, data in model_links.items():
            print(get_model_row(current_compat, name, data, 'link'))
    else:
        prints(Messages.M024, exits=0)
    if update_models:
        cmd = '    python -m spacy download {}'
        print("\n    " + Messages.M025)
        print('\n'.join([cmd.format(pkg) for pkg in update_models]))
    if na_models:
        prints(Messages.M025.format(version=about.__version__,
                                    models=', '.join(na_models)))
    if incompat_links:
        prints(Messages.M027.format(path=path2str(get_data_path())))
    if incompat_models or incompat_links:
        sys.exit(1)


def get_model_links(compat):
    links = {}
    data_path = get_data_path()
    if data_path:
        models = [p for p in data_path.iterdir() if is_model_path(p)]
        for model in models:
            meta_path = Path(model) / 'meta.json'
            if not meta_path.exists():
                continue
            meta = read_json(meta_path)
            link = model.parts[-1]
            name = meta['lang'] + '_' + meta['name']
            links[link] = {'name': name, 'version': meta['version'],
                           'compat': is_compat(compat, name, meta['version'])}
    return links


def get_model_pkgs(compat, all_models):
    pkgs = {}
    for pkg_name, pkg_data in pkg_resources.working_set.by_key.items():
        package = pkg_name.replace('-', '_')
        if package in all_models:
            version = pkg_data.version
            pkgs[pkg_name] = {'name': package, 'version': version,
                              'compat': is_compat(compat, package, version)}
    return pkgs


def get_model_row(compat, name, data, type='package'):
    tpl_red = '\x1b[38;5;1m{}\x1b[0m'
    tpl_green = '\x1b[38;5;2m{}\x1b[0m'
    if data['compat']:
        comp = tpl_green.format(locale_escape('✔', errors='ignore'))
        version = tpl_green.format(data['version'])
    else:
        comp = '--> {}'.format(compat.get(data['name'], ['n/a'])[0])
        version = tpl_red.format(data['version'])
    return get_row(type, name, data['name'], version, comp)


def get_row(*args):
    tpl_row = '    {:<10}' + ('  {:<20}' * 4)
    return tpl_row.format(*args)


def is_model_path(model_path):
    exclude = ['cache', 'pycache', '__pycache__']
    name = model_path.parts[-1]
    return (model_path.is_dir() and name not in exclude
            and not name.startswith('.'))


def is_compat(compat, name, version):
    return name in compat and version in compat[name]


def reformat_version(version):
    """Hack to reformat old versions ending on '-alpha' to match pip format."""
    if version.endswith('-alpha'):
        return version.replace('-alpha', 'a0')
    return version.replace('-alpha', 'a')

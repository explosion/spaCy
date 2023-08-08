import React, { useState } from 'react'

import { Quickstart, QS } from '../components/quickstart'
import { repo, DEFAULT_BRANCH } from '../components/util'
import siteMetadata from '../../meta/site.json'
import models from '../../meta/languages.json'

const DEFAULT_OS = 'mac'
const DEFAULT_PLATFORM = 'x86'
const DEFAULT_MODELS = ['en']
const DEFAULT_OPT = 'efficiency'
const DEFAULT_HARDWARE = 'cpu'
const DEFAULT_CUDA = 'cuda11x'
const CUDA = {
    '8.0': 'cuda80',
    '9.0': 'cuda90',
    '9.1': 'cuda91',
    '9.2': 'cuda92',
    '10.0': 'cuda100',
    '10.1': 'cuda101',
    '10.2': 'cuda102',
    '11.0': 'cuda110',
    '11.1': 'cuda111',
    '11.2-11.x': 'cuda11x',
    '12.x': 'cuda12x',
}
const LANG_EXTRAS = ['ja'] // only for languages with models

const QuickstartInstall = ({ id, title }) => {
    const [train, setTrain] = useState(false)
    const [platform, setPlatform] = useState(DEFAULT_PLATFORM)
    const [os, setOs] = useState(DEFAULT_OS)
    const [hardware, setHardware] = useState(DEFAULT_HARDWARE)
    const [cuda, setCuda] = useState(DEFAULT_CUDA)
    const [selectedModels, setModels] = useState(DEFAULT_MODELS)
    const [efficiency, setEfficiency] = useState(DEFAULT_OPT === 'efficiency')
    const setters = {
        hardware: (v) => (Array.isArray(v) ? setHardware(v[0]) : setCuda(v)),
        config: (v) => setTrain(v.includes('train')),
        models: setModels,
        optimize: (v) => setEfficiency(v.includes('efficiency')),
        platform: (v) => setPlatform(v[0]),
        os: (v) => setOs(v[0]),
    }
    const showDropdown = {
        hardware: () => hardware === 'gpu',
    }
    const modelExtras = train ? selectedModels.filter((m) => LANG_EXTRAS.includes(m)) : []
    const apple = os === 'mac' && platform === 'arm'
    const pipExtras = [
        hardware === 'gpu' && (platform !== 'arm' || os === 'linux') && cuda,
        train && 'transformers',
        train && 'lookups',
        apple && 'apple',
        ...modelExtras,
    ]
        .filter((e) => e)
        .join(',')

    const { nightly } = siteMetadata
    const pkg = nightly ? 'spacy-nightly' : 'spacy'
    const languages = models.languages.filter(({ models }) => !!models)
    const data = [
        {
            id: 'os',
            title: 'Operating system',
            options: [
                { id: 'mac', title: 'macOS / OSX', checked: true },
                { id: 'windows', title: 'Windows' },
                { id: 'linux', title: 'Linux' },
            ],
            defaultValue: DEFAULT_OS,
        },
        {
            id: 'platform',
            title: 'Platform',
            options: [
                { id: 'x86', title: 'x86', checked: true },
                { id: 'arm', title: 'ARM / M1' },
            ],
            defaultValue: DEFAULT_PLATFORM,
        },
        {
            id: 'package',
            title: 'Package manager',
            options: [
                { id: 'pip', title: 'pip', checked: true },
                !nightly ? { id: 'conda', title: 'conda' } : null,
                { id: 'source', title: 'from source' },
            ].filter((o) => o),
        },
        {
            id: 'hardware',
            title: 'Hardware',
            options: [
                { id: 'cpu', title: 'CPU', checked: DEFAULT_HARDWARE === 'cpu' },
                { id: 'gpu', title: 'GPU', checked: DEFAULT_HARDWARE == 'gpu' },
            ],
            dropdown: Object.keys(CUDA).map((id) => ({
                id: CUDA[id],
                title: `CUDA ${id}`,
            })),
            defaultValue: DEFAULT_CUDA,
        },
        {
            id: 'config',
            title: 'Configuration',
            multiple: true,
            options: [
                {
                    id: 'venv',
                    title: 'virtual env',
                    help: 'Use a virtual environment',
                },
                {
                    id: 'train',
                    title: 'train models',
                    help: 'Check this if you plan to train your own models with spaCy to install extra dependencies and data resources',
                },
            ],
        },
        {
            id: 'models',
            title: 'Trained pipelines',
            multiple: true,
            options: languages
                .sort((a, b) => a.name.localeCompare(b.name))
                .map(({ code, name }) => ({
                    id: code,
                    title: name,
                    checked: DEFAULT_MODELS.includes(code),
                })),
        },
    ]
    if (selectedModels.length) {
        data.push({
            id: 'optimize',
            title: 'Select pipeline for',
            options: [
                {
                    id: 'efficiency',
                    title: 'efficiency',
                    checked: DEFAULT_OPT === 'efficiency',
                    help: 'Faster and smaller pipeline, but less accurate',
                },
                {
                    id: 'accuracy',
                    title: 'accuracy',
                    checked: DEFAULT_OPT === 'accuracy',
                    help: 'Larger and slower pipeline, but more accurate',
                },
            ],
        })
    }
    return (
        <Quickstart data={data} title={title} id={id} setters={setters} showDropdown={showDropdown}>
            <QS os="mac" hardware="gpu" platform="arm" comment prompt={false}>
                # Note M1 GPU support is experimental, see{' '}
                <a href="https://github.com/explosion/thinc/issues/792">Thinc issue #792</a>
            </QS>
            <QS package="pip" config="venv">
                python -m venv .env
            </QS>
            <QS package="pip" config="venv" os="mac">
                source .env/bin/activate
            </QS>
            <QS package="pip" config="venv" os="linux">
                source .env/bin/activate
            </QS>
            <QS package="pip" config="venv" os="windows">
                .env\Scripts\activate
            </QS>
            <QS package="source" config="venv">
                python -m venv .env
            </QS>
            <QS package="source" config="venv" os="mac">
                source .env/bin/activate
            </QS>
            <QS package="source" config="venv" os="linux">
                source .env/bin/activate
            </QS>
            <QS package="source" config="venv" os="windows">
                .env\Scripts\activate
            </QS>
            <QS package="conda" config="venv">
                conda create -n venv
            </QS>
            <QS package="conda" config="venv">
                conda activate venv
            </QS>
            <QS package="pip">pip install -U pip setuptools wheel</QS>
            <QS package="source">pip install -U pip setuptools wheel</QS>
            <QS package="pip">
                {pipExtras ? `pip install -U '${pkg}[${pipExtras}]'` : `pip install -U ${pkg}`}
                {nightly ? ' --pre' : ''}
            </QS>
            <QS package="conda">conda install -c conda-forge spacy</QS>
            <QS package="conda" hardware="gpu">
                conda install -c conda-forge cupy
            </QS>
            <QS package="conda" config="train">
                conda install -c conda-forge spacy-transformers
            </QS>
            <QS package="source">
                git clone https://github.com/{repo}
                {nightly ? ` --branch ${DEFAULT_BRANCH}` : ''}
            </QS>
            <QS package="source">cd spaCy</QS>
            <QS package="source">pip install -r requirements.txt</QS>
            <QS package="source">
                pip install --no-build-isolation --editable{' '}
                {train || hardware == 'gpu' ? `'.[${pipExtras}]'` : '.'}
            </QS>
            <QS config="train" package="conda" comment prompt={false}>
                # packages only available via pip
            </QS>
            <QS config="train" package="conda">
                pip install spacy-lookups-data
            </QS>

            {languages.map(({ code, models: modelOptions }) => {
                const pkg = modelOptions[efficiency ? 0 : modelOptions.length - 1]
                return (
                    <QS models={code} key={code}>
                        python -m spacy download {pkg}
                    </QS>
                )
            })}
        </Quickstart>
    )
}

export default QuickstartInstall

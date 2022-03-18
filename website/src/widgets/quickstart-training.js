import React, { useState } from 'react'
import { StaticQuery, graphql } from 'gatsby'
import highlightCode from 'gatsby-remark-prismjs/highlight-code.js'

import { Quickstart } from '../components/quickstart'
import generator, { DATA as GENERATOR_DATA } from './quickstart-training-generator'
import { htmlToReact } from '../components/util'

const DEFAULT_LANG = 'en'
const DEFAULT_HARDWARE = 'cpu'
const DEFAULT_OPT = 'efficiency'
const DEFAULT_TEXTCAT_EXCLUSIVE = true
const COMPONENTS = ['tagger', 'morphologizer', 'trainable_lemmatizer', 'parser', 'ner', 'spancat', 'textcat']
const COMMENT = `# This is an auto-generated partial config. To use it with 'spacy train'
# you can run spacy init fill-config to auto-fill all default settings:
# python -m spacy init fill-config ./base_config.cfg ./config.cfg`

const DATA = [
    {
        id: 'lang',
        title: 'Language',
        defaultValue: DEFAULT_LANG,
    },
    {
        id: 'components',
        title: 'Components',
        help: 'Pipeline components to train. Requires training data for those annotations.',
        options: COMPONENTS.map(id => ({ id, title: id })),
        multiple: true,
    },
    {
        id: 'textcat',
        title: 'Text Classification',
        multiple: true,
        options: [
            {
                id: 'exclusive',
                title: 'exclusive categories',
                checked: DEFAULT_TEXTCAT_EXCLUSIVE,
                help: 'only one label can apply',
            },
        ],
    },
    {
        id: 'hardware',
        title: 'Hardware',
        options: [
            { id: 'cpu', title: 'CPU', checked: DEFAULT_HARDWARE === 'cpu' },
            { id: 'gpu', title: 'GPU (transformer)', checked: DEFAULT_HARDWARE === 'gpu' },
        ],
    },
    {
        id: 'optimize',
        title: 'Optimize for',
        help:
            'Optimize for efficiency (faster inference, smaller model, lower memory consumption) or higher accuracy (potentially larger & slower model). Will impact the choice of architecture, pretrained weights and hyperparameters.',
        options: [
            { id: 'efficiency', title: 'efficiency', checked: DEFAULT_OPT === 'efficiency' },
            { id: 'accuracy', title: 'accuracy', checked: DEFAULT_OPT === 'accuracy' },
        ],
    },
]

export default function QuickstartTraining({ id, title, download = 'base_config.cfg' }) {
    const [lang, setLang] = useState(DEFAULT_LANG)
    const [_components, _setComponents] = useState([])
    const [components, setComponents] = useState([])
    const [[hardware], setHardware] = useState([DEFAULT_HARDWARE])
    const [[optimize], setOptimize] = useState([DEFAULT_OPT])
    const [textcatExclusive, setTextcatExclusive] = useState(DEFAULT_TEXTCAT_EXCLUSIVE)

    function updateComponents(value, isExclusive) {
        _setComponents(value)
        const updated = value.map(c => (c === 'textcat' && !isExclusive ? 'textcat_multilabel' : c))
        setComponents(updated)
    }

    const setters = {
        lang: setLang,
        components: v => updateComponents(v, textcatExclusive),
        hardware: setHardware,
        optimize: setOptimize,
        textcat: v => {
            const isExclusive = v.includes('exclusive')
            setTextcatExclusive(isExclusive)
            updateComponents(_components, isExclusive)
        },
    }
    const defaultData = GENERATOR_DATA.__default__
    const reco = GENERATOR_DATA[lang] || defaultData
    const content = generator({
        lang,
        components,
        optimize,
        hardware,
        transformer_data: reco.transformer || defaultData.transformer,
        word_vectors: reco.word_vectors,
        has_letters: reco.has_letters,
    })
    const rawStr = content.trim().replace(/\n\n\n+/g, '\n\n')
    const rawContent = `${COMMENT}\n${rawStr}`
    const displayContent = highlightCode('ini', rawContent)
        .split('\n')
        .map(line => (line.startsWith('#') ? `<span class="token comment">${line}</span>` : line))
        .join('\n')
    return (
        <StaticQuery
            query={query}
            render={({ site }) => {
                let data = DATA
                const langs = site.siteMetadata.languages
                data[0].dropdown = langs
                    .map(({ name, code }) => ({
                        id: code,
                        title: name,
                    }))
                    .sort((a, b) => a.title.localeCompare(b.title))
                if (!_components.includes('textcat')) {
                    data = data.map(field =>
                        field.id === 'textcat' ? { ...field, hidden: true } : field
                    )
                }
                return (
                    <Quickstart
                        id="quickstart-widget"
                        Container="div"
                        download={download}
                        rawContent={rawContent}
                        data={data}
                        title={title}
                        id={id}
                        setters={setters}
                        hidePrompts
                        small
                        codeLang="ini"
                    >
                        {htmlToReact(displayContent)}
                    </Quickstart>
                )
            }}
        />
    )
}

const query = graphql`
    query QuickstartTrainingQuery {
        site {
            siteMetadata {
                languages {
                    code
                    name
                }
            }
        }
    }
`

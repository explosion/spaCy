import React, { useState } from 'react'
import { StaticQuery, graphql } from 'gatsby'
import highlightCode from 'gatsby-remark-prismjs/highlight-code.js'

import { Quickstart } from '../components/quickstart'
import generator, { DATA as GENERATOR_DATA } from './quickstart-training-generator'
import { htmlToReact } from '../components/util'

const DEFAULT_LANG = 'en'
const DEFAULT_HARDWARE = 'gpu'
const DEFAULT_OPT = 'efficiency'
const COMPONENTS = ['tagger', 'parser', 'ner', 'textcat']
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
        id: 'hardware',
        title: 'Hardware',
        options: [
            { id: 'cpu', title: 'CPU preferred', checked: DEFAULT_HARDWARE === 'cpu' },
            { id: 'gpu', title: 'GPU', checked: DEFAULT_HARDWARE === 'gpu' },
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
    const [components, setComponents] = useState([])
    const [[hardware], setHardware] = useState([DEFAULT_HARDWARE])
    const [[optimize], setOptimize] = useState([DEFAULT_OPT])
    const setters = {
        lang: setLang,
        components: setComponents,
        hardware: setHardware,
        optimize: setOptimize,
    }
    const reco = GENERATOR_DATA[lang] || {}
    const content = generator({
        lang,
        components,
        optimize,
        hardware,
        transformer_data: reco.transformer,
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
                const langs = site.siteMetadata.languages
                DATA[0].dropdown = langs
                    .map(({ name, code }) => ({
                        id: code,
                        title: name,
                    }))
                    .sort((a, b) => a.title.localeCompare(b.title))
                return (
                    <Quickstart
                        id="quickstart-widget"
                        Container="div"
                        download={download}
                        rawContent={content}
                        data={DATA}
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

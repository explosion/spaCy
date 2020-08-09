import React, { useState } from 'react'
import { StaticQuery, graphql } from 'gatsby'

import { Quickstart, QS } from '../components/quickstart'

const DEFAULT_LANG = 'en'
const COMPONENTS = ['tagger', 'parser', 'ner', 'textcat']
const COMMENT = `# This is an auto-generated partial config for training a model.
# To use it for training, auto-fill it with all default values.
# python -m spacy init config config.cfg --base base_config.cfg`
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
            { id: 'cpu-only', title: 'CPU only' },
            { id: 'cpu', title: 'CPU preferred' },
            { id: 'gpu', title: 'GPU', checked: true },
        ],
    },
    {
        id: 'optimize',
        title: 'Optimize for',
        help: '...',
        options: [
            { id: 'efficiency', title: 'efficiency', checked: true },
            { id: 'accuracy', title: 'accuracy' },
        ],
    },
    {
        id: 'config',
        title: 'Configuration',
        options: [
            {
                id: 'independent',
                title: 'independent components',
                help: "Make components independent and don't share weights",
            },
        ],
        multiple: true,
    },
]

export default function QuickstartTraining({ id, title, download = 'config.cfg' }) {
    const [lang, setLang] = useState(DEFAULT_LANG)
    const [pipeline, setPipeline] = useState([])
    const setters = { lang: setLang, components: setPipeline }
    return (
        <StaticQuery
            query={query}
            render={({ site }) => {
                const langs = site.siteMetadata.languages
                DATA[0].dropdown = langs.map(({ name, code }) => ({
                    id: code,
                    title: name,
                }))
                const recommendedTrf = Object.assign(
                    {},
                    ...langs.map(({ code }) => ({ [code]: { sm: 'TODO', lg: 'TODO' } }))
                )
                return (
                    <Quickstart
                        download={download}
                        data={DATA}
                        title={title}
                        id={id}
                        setters={setters}
                        hidePrompts
                    >
                        <QS comment>{COMMENT}</QS>
                        <span>[paths]</span>
                        <span>train = ""</span>
                        <span>dev = ""</span>
                        <br />
                        <span>[nlp]</span>
                        <span>lang = "{lang}"</span>
                        <span>pipeline = {JSON.stringify(pipeline).replace(/,/g, ', ')}</span>
                        <br />
                        <span>[components]</span>
                        <br />
                        <span>[components.transformer]</span>
                        <QS optimize="efficiency">name = "{recommendedTrf[lang].sm}"</QS>
                        <QS optimize="accuracy">name = "{recommendedTrf[lang].lg}"</QS>
                        {!!pipeline.length && <br />}
                        {pipeline.map((pipe, i) => (
                            <>
                                {i !== 0 && <br />}
                                <span>[components.{pipe}]</span>
                                <span>factory = "{pipe}"</span>
                                <QS config="independent">
                                    <br />
                                    [components.parser.model.tok2vec]
                                    <br />
                                    @architectures = "spacy.Tok2Vec.v1"
                                </QS>
                            </>
                        ))}
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

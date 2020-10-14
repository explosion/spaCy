import React, { Fragment, useState } from 'react'
import { StaticQuery, graphql } from 'gatsby'

import { Quickstart, QS } from '../components/quickstart'

const DEFAULT_LANG = 'en'
const DEFAULT_OPT = 'efficiency'

const data = [
    {
        id: 'lang',
        title: 'Language',
        defaultValue: DEFAULT_LANG,
    },
    {
        id: 'load',
        title: 'Loading style',
        options: [
            {
                id: 'spacy',
                title: 'Use spacy.load()',
                help: "Use spaCy's built-in loader to load the package by name",
                checked: true,
            },
            {
                id: 'module',
                title: 'Import as module',
                help: 'Import the package explicitly as a Python module',
            },
        ],
    },
    {
        id: 'optimize',
        title: 'Select for',
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
    },
    {
        id: 'config',
        title: 'Options',
        multiple: true,
        options: [{ id: 'example', title: 'Show text example' }],
    },
]

const QuickstartInstall = ({ id, title, description, children }) => {
    const [lang, setLang] = useState(DEFAULT_LANG)
    const [efficiency, setEfficiency] = useState(DEFAULT_OPT === 'efficiency')
    const setters = {
        lang: setLang,
        optimize: v => setEfficiency(v.includes('efficiency')),
    }
    return (
        <StaticQuery
            query={query}
            render={({ site }) => {
                const models = site.siteMetadata.languages.filter(({ models }) => models !== null)
                data[0].dropdown = models
                    .sort((a, b) => a.name.localeCompare(b.name))
                    .map(({ code, name }) => ({
                        id: code,
                        title: name,
                    }))
                return (
                    <Quickstart
                        data={data}
                        title={title}
                        id={id}
                        description={description}
                        setters={setters}
                        copy={false}
                    >
                        {models.map(({ code, models, example }) => {
                            const pkg = efficiency ? models[0] : models[models.length - 1]
                            const exampleText = example || 'No text available yet'
                            return lang !== code ? null : (
                                <Fragment key={code}>
                                    <QS>python -m spacy download {pkg}</QS>
                                    <QS divider />
                                    <QS load="spacy" prompt="python">
                                        import spacy
                                    </QS>
                                    <QS load="spacy" prompt="python">
                                        nlp = spacy.load("{pkg}")
                                    </QS>
                                    <QS load="module" prompt="python">
                                        import {pkg}
                                    </QS>
                                    <QS load="module" prompt="python">
                                        nlp = {pkg}.load()
                                    </QS>
                                    <QS config="example" prompt="python">
                                        doc = nlp("{exampleText}")
                                    </QS>
                                    <QS config="example" prompt="python">
                                        print([
                                        {code === 'xx'
                                            ? '(ent.text, ent.label) for ent in doc.ents'
                                            : '(w.text, w.pos_) for w in doc'}
                                        ])
                                    </QS>
                                </Fragment>
                            )
                        })}

                        {children}
                    </Quickstart>
                )
            }}
        />
    )
}

export default QuickstartInstall

const query = graphql`
    query QuickstartModelsQuery {
        site {
            siteMetadata {
                languages {
                    code
                    name
                    models
                    example
                }
            }
        }
    }
`

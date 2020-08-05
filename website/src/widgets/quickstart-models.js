import React, { Fragment } from 'react'
import { StaticQuery, graphql } from 'gatsby'

import { Quickstart, QS } from '../components/quickstart'

const data = [
    {
        id: 'lang',
        title: 'Language',
    },
    {
        id: 'load',
        title: 'Loading style',
        options: [
            {
                id: 'spacy',
                title: 'Use spacy.load()',
                help: "Use spaCy's built-in loader to load the model by name.",
                checked: true,
            },
            {
                id: 'module',
                title: 'Import as module',
                help: 'Import the model explicitly as a Python module.',
            },
        ],
    },
    {
        id: 'config',
        title: 'Options',
        multiple: true,
        options: [{ id: 'example', title: 'Show usage example' }],
    },
]

const QuickstartInstall = ({ id, title, description, defaultLang = 'en', children }) => (
    <StaticQuery
        query={query}
        render={({ site }) => {
            const models = site.siteMetadata.languages.filter(({ models }) => models !== null)
            data[0].options = models.map(({ code, name }) => ({
                id: code,
                title: name,
                checked: code === defaultLang,
            }))
            return (
                <Quickstart data={data} title={title} id={id} description={description}>
                    {models.map(({ code, models, example }) => {
                        const pkg = models[0]
                        const exampleText = example || 'No text available yet'
                        return (
                            <Fragment key={code}>
                                <QS lang={code}>python -m spacy download {pkg}</QS>
                                <QS lang={code} divider />
                                <QS lang={code} load="spacy" prompt="python">
                                    import spacy
                                </QS>
                                <QS lang={code} load="spacy" prompt="python">
                                    nlp = spacy.load("{pkg}")
                                </QS>
                                <QS lang={code} load="module" prompt="python">
                                    import {pkg}
                                </QS>
                                <QS lang={code} load="module" prompt="python">
                                    nlp = {pkg}.load()
                                </QS>
                                <QS lang={code} config="example" prompt="python">
                                    doc = nlp("{exampleText}")
                                </QS>
                                <QS lang={code} config="example" prompt="python">
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

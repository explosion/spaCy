import React from 'react'
import { StaticQuery, graphql } from 'gatsby'

import Link from '../components/link'
import { InlineCode } from '../components/code'
import { Table, Tr, Th, Td } from '../components/table'
import { Ul, Li } from '../components/list'
import Infobox from '../components/infobox'
import { github, join } from '../components/util'

const Language = ({ name, code, models }) => (
    <Tr>
        <Td>{name}</Td>
        <Td>
            <InlineCode>{code}</InlineCode>
        </Td>
        <Td>
            <Link to={github(`spacy/lang/${code}`)}>
                <InlineCode>lang/{code}</InlineCode>
            </Link>
        </Td>
        <Td>
            {models && models.length ? (
                <Link to={`/models/${code}`}>
                    {models.length} {models.length === 1 ? 'package' : 'packages'}
                </Link>
            ) : (
                <em>none yet</em>
            )}
        </Td>
    </Tr>
)

const Languages = () => (
    <StaticQuery
        query={query}
        render={({ site }) => {
            const langs = site.siteMetadata.languages
            const withModels = langs
                .filter(({ models }) => models && !!models.length)
                .sort((a, b) => a.name.localeCompare(b.name))
            const withoutModels = langs
                .filter(({ models }) => !models || !models.length)
                .sort((a, b) => a.name.localeCompare(b.name))
            const withDeps = langs.filter(({ dependencies }) => dependencies && dependencies.length)
            return (
                <>
                    <Table>
                        <thead>
                            <Tr>
                                <Th>Language</Th>
                                <Th>Code</Th>
                                <Th>Language Data</Th>
                                <Th>Pipelines</Th>
                            </Tr>
                        </thead>
                        <tbody>
                            {withModels.map(model => (
                                <Language {...model} key={model.code} />
                            ))}
                            {withoutModels.map(model => (
                                <Language {...model} key={model.code} />
                            ))}
                        </tbody>
                    </Table>
                    <Infobox title="Dependencies">
                        <p>Some language tokenizers require external dependencies.</p>
                        <Ul>
                            {withDeps.map(({ code, name, dependencies }) => (
                                <Li key={code}>
                                    <strong>{name}:</strong>{' '}
                                    {join(
                                        dependencies.map((dep, i) => (
                                            <Link to={dep.url}>{dep.name}</Link>
                                        ))
                                    )}
                                </Li>
                            ))}
                        </Ul>
                    </Infobox>
                </>
            )
        }}
    />
)

export default Languages

const query = graphql`
    query LanguagesQuery {
        site {
            siteMetadata {
                languages {
                    code
                    name
                    models
                    dependencies {
                        name
                        url
                    }
                }
            }
        }
    }
`

import React from 'react'
import PropTypes from 'prop-types'
import { StaticQuery, graphql } from 'gatsby'

import Models from './models'

import ReadNext from '../components/readnext'
import Button from '../components/button'
import Grid from '../components/grid'
import Title from '../components/title'
import Footer from '../components/footer'
import Sidebar from '../components/sidebar'
import Main from '../components/main'
import { getCurrentSource, github } from '../components/util'

const Docs = ({ pageContext, children }) => (
    <StaticQuery
        query={query}
        render={({ site }) => {
            const {
                id,
                slug,
                title,
                section,
                teaser,
                source,
                tag,
                isIndex,
                next,
                menu,
                theme,
                version,
                apiDetails,
            } = pageContext
            const { sidebars = [], modelsRepo, languages, nightly, legacy } = site.siteMetadata
            const isModels = section === 'models'
            const sidebar = pageContext.sidebar
                ? { items: pageContext.sidebar }
                : sidebars.find(bar => bar.section === section)
            let pageMenu = menu ? menu.map(([text, id]) => ({ text, id })) : []

            if (isModels) {
                sidebar.items[1].items = languages
                    .filter(({ models }) => models && models.length)
                    .sort((a, b) => a.name.localeCompare(b.name))
                    .map(lang => ({
                        text: lang.name,
                        url: `/models/${lang.code}`,
                        isActive: id === lang.code,
                        menu: lang.models.map(model => ({
                            text: model,
                            id: model,
                        })),
                    }))
            }
            const sourcePath = source ? github(source) : null
            const currentSource = getCurrentSource(slug, isIndex)

            const subFooter = (
                <Grid cols={2}>
                    <div style={{ marginTop: 'var(--spacing-lg)' }}>
                        {(!isModels || (isModels && isIndex)) && (
                            <Button to={currentSource} icon="code">
                                Suggest edits
                            </Button>
                        )}
                    </div>
                    {next && <ReadNext title={next.title} to={next.slug} />}
                </Grid>
            )

            return (
                <>
                    {sidebar && <Sidebar items={sidebar.items} pageMenu={pageMenu} slug={slug} />}
                    <Main
                        section={section}
                        theme={nightly ? 'nightly' : legacy ? 'legacy' : theme}
                        sidebar
                        asides
                        wrapContent
                        footer={<Footer />}
                    >
                        {isModels && !isIndex ? (
                            <Models pageContext={pageContext} repo={modelsRepo}>
                                {subFooter}
                            </Models>
                        ) : (
                            <>
                                <Title
                                    title={title}
                                    teaser={teaser}
                                    source={sourcePath}
                                    tag={tag}
                                    version={version}
                                    id="_title"
                                    apiDetails={apiDetails}
                                />
                                {children}
                                {subFooter}
                            </>
                        )}
                    </Main>
                </>
            )
        }}
    />
)

Docs.propTypes = {
    pageContext: PropTypes.shape({
        slug: PropTypes.string.isRequired,
        title: PropTypes.string.isRequired,
        section: PropTypes.string,
        teaser: PropTypes.string,
        source: PropTypes.string,
        tag: PropTypes.string,
        isIndex: PropTypes.bool,
        next: PropTypes.shape({
            title: PropTypes.string.isRequired,
            slug: PropTypes.string.isRequired,
        }),
        menu: PropTypes.arrayOf(PropTypes.arrayOf(PropTypes.string)),
        theme: PropTypes.string,
    }),
}

export default Docs

const query = graphql`
    query DocsQuery {
        site {
            siteMetadata {
                repo
                modelsRepo
                languages {
                    code
                    name
                    models
                }
                nightly
                legacy
                sidebars {
                    section
                    items {
                        label
                        items {
                            text
                            url
                            tag
                        }
                    }
                }
            }
        }
    }
`

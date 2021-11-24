import React from 'react'
import PropTypes from 'prop-types'
import { graphql } from 'gatsby'
import { MDXProvider } from '@mdx-js/tag'
import { withMDXScope } from 'gatsby-mdx/context'
import useOnlineStatus from '@rehooks/online-status'
import classNames from 'classnames'

import MDXRenderer from './mdx-renderer'

// Templates
import Docs from './docs'
import Universe from './universe'

// Components
import Navigation from '../components/navigation'
import Progress from '../components/progress'
import Footer from '../components/footer'
import SEO from '../components/seo'
import Link from '../components/link'
import Section, { Hr } from '../components/section'
import { Table, Tr, Th, Tx, Td } from '../components/table'
import { Pre, Code, InlineCode, TypeAnnotation } from '../components/code'
import { Ol, Ul, Li } from '../components/list'
import { H2, H3, H4, H5, P, Abbr, Help } from '../components/typography'
import Accordion from '../components/accordion'
import Infobox from '../components/infobox'
import Aside from '../components/aside'
import Button from '../components/button'
import Tag from '../components/tag'
import Grid from '../components/grid'
import { YouTube, SoundCloud, Iframe, Image } from '../components/embed'
import Alert from '../components/alert'
import Search from '../components/search'
import Project from '../widgets/project'
import { Integration, IntegrationLogo } from '../widgets/integration'

const mdxComponents = {
    a: Link,
    p: P,
    pre: Pre,
    code: Code,
    inlineCode: InlineCode,
    del: TypeAnnotation,
    table: Table,
    img: Image,
    tr: Tr,
    th: Th,
    td: Td,
    ol: Ol,
    ul: Ul,
    li: Li,
    h2: H2,
    h3: H3,
    h4: H4,
    h5: H5,
    blockquote: Aside,
    section: Section,
    wrapper: ({ children }) => children,
    hr: Hr,
}

const scopeComponents = {
    Infobox,
    Table,
    Tr,
    Tx,
    Th,
    Td,
    Help,
    Button,
    YouTube,
    SoundCloud,
    Iframe,
    Abbr,
    Tag,
    Accordion,
    Grid,
    InlineCode,
    Project,
    Integration,
    IntegrationLogo,
}

const AlertSpace = ({ nightly, legacy }) => {
    const isOnline = useOnlineStatus()
    return (
        <>
            {nightly && (
                <Alert
                    title="You're viewing the pre-release docs."
                    icon="moon"
                    closeOnClick={false}
                >
                    The page reflects{' '}
                    <Link to="https://pypi.org/project/spacy-nightly/">
                        <InlineCode>spacy-nightly</InlineCode>
                    </Link>
                    , not the latest <Link to="https://spacy.io">stable version</Link>.
                </Alert>
            )}
            {legacy && (
                <Alert
                    title="You're viewing the old documentation"
                    icon="warning"
                    closeOnClick={false}
                >
                    The page reflects an older version of spaCy, not the latest{' '}
                    <Link to="https://spacy.io">stable release</Link>.
                </Alert>
            )}
            {!isOnline && (
                <Alert title="Looks like you're offline." icon="offline" variant="warning">
                    But don't worry, your visited pages should be saved for you.
                </Alert>
            )}
        </>
    )
}

const navAlert = (
    <Link to="/usage/v3-2" hidden>
        <strong>💥 Out now:</strong> spaCy v3.2
    </Link>
)

class Layout extends React.Component {
    static defaultProps = {
        scope: {},
    }

    static propTypes = {
        data: PropTypes.shape({
            mdx: PropTypes.shape({
                code: PropTypes.shape({
                    body: PropTypes.string.isRequired,
                }).isRequired,
            }),
        }).isRequired,
        scope: PropTypes.object.isRequired,
        pageContext: PropTypes.shape({
            title: PropTypes.string,
            section: PropTypes.string,
            teaser: PropTypes.string,
            source: PropTypes.string,
            isIndex: PropTypes.bool.isRequired,
            theme: PropTypes.string,
            searchExclude: PropTypes.bool,
            next: PropTypes.shape({
                title: PropTypes.string.isRequired,
                slug: PropTypes.string.isRequired,
            }),
        }),
        children: PropTypes.node,
    }

    constructor(props) {
        super(props)
        // NB: Compiling the scope here instead of in render() is super
        // important! Otherwise, it triggers unnecessary rerenders of ALL
        // consumers (e.g. mdx elements), even on anchor navigation!
        this.state = { scope: { ...scopeComponents, ...props.scope } }
    }

    render() {
        const { data, pageContext, location, children } = this.props
        const { file, site = {} } = data || {}
        const mdx = file ? file.childMdx : null
        const meta = site.siteMetadata || {}
        const { title, section, sectionTitle, teaser, theme = 'blue', searchExclude } = pageContext
        const uiTheme = meta.nightly ? 'nightly' : meta.legacy ? 'legacy' : theme
        const bodyClass = classNames(`theme-${uiTheme}`, { 'search-exclude': !!searchExclude })
        const isDocs = ['usage', 'models', 'api', 'styleguide'].includes(section)
        const content = !mdx ? null : (
            <MDXProvider components={mdxComponents}>
                <MDXRenderer scope={this.state.scope}>{mdx.code.body}</MDXRenderer>
            </MDXProvider>
        )

        return (
            <>
                <SEO
                    title={title}
                    description={teaser || meta.description}
                    section={section}
                    sectionTitle={sectionTitle}
                    bodyClass={bodyClass}
                    nightly={meta.nightly}
                />
                <AlertSpace nightly={meta.nightly} legacy={meta.legacy} />
                <Navigation
                    title={meta.title}
                    items={meta.navigation}
                    section={section}
                    search={<Search settings={meta.docSearch} />}
                    alert={meta.nightly ? null : navAlert}
                >
                    <Progress key={location.href} />
                </Navigation>
                {isDocs ? (
                    <Docs pageContext={pageContext}>{content}</Docs>
                ) : section === 'universe' ? (
                    <Universe
                        pageContext={pageContext}
                        location={location}
                        mdxComponents={mdxComponents}
                    />
                ) : (
                    <div>
                        {children}
                        {content}
                        <Footer wide />
                    </div>
                )}
            </>
        )
    }
}

export default withMDXScope(Layout)

export const pageQuery = graphql`
    query($slug: String!) {
        site {
            siteMetadata {
                nightly
                legacy
                title
                description
                navigation {
                    text
                    url
                }
                docSearch {
                    apiKey
                    indexName
                }
            }
        }
        file(fields: { slug: { eq: $slug } }) {
            childMdx {
                code {
                    scope
                    body
                }
            }
        }
    }
`

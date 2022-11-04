import React from 'react'
import PropTypes from 'prop-types'
import useOnlineStatus from '@rehooks/online-status'
import classNames from 'classnames'

// Templates
import Docs from './docs'
import Universe from './universe'

// Components
import Navigation from '../navigation'
import Progress from '../progress'
import Footer from '../footer'
import SEO from '../seo'
import Link from '../link'
import Section, { Hr } from '../section'
import { Table, Tr, Th, Tx, Td } from '../table'
import { Pre, Code, InlineCode, TypeAnnotation } from '../code'
import { Ol, Ul, Li } from '../list'
import { H2, H3, H4, H5, P, Abbr, Help } from '../typography'
import Accordion from '../accordion'
import Infobox from '../infobox'
import Aside from '../aside'
import Button from '../button'
import Tag from '../tag'
import Grid from '../grid'
import { YouTube, SoundCloud, Iframe, Image, GoogleSheet } from '../embed'
import Alert from '../alert'
import Search from '../search'
import Project from '../../widgets/project'
import { Integration, IntegrationLogo } from '../../widgets/integration'

import siteMetadata from '../../../meta/site.json'
import { nightly, legacy } from '../../../meta/dynamicMeta'

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
    GoogleSheet,
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
    <Link to="/usage/v3-4" hidden>
        <strong>💥 Out now:</strong> spaCy v3.4
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
        const { title, section, sectionTitle, teaser, theme = 'blue', searchExclude } = pageContext
        const uiTheme = nightly ? 'nightly' : legacy ? 'legacy' : theme
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
                    description={teaser || siteMetadata.description}
                    section={section}
                    sectionTitle={sectionTitle}
                    bodyClass={bodyClass}
                    nightly={nightly}
                />
                <AlertSpace nightly={nightly} legacy={legacy} />
                <Navigation
                    title={siteMetadata.title}
                    items={siteMetadata.navigation}
                    section={section}
                    search={<Search settings={siteMetadata.docSearch} />}
                    alert={nightly ? null : navAlert}
                >
                    <Progress />
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

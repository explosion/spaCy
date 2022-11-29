import React from 'react'
import PropTypes from 'prop-types'
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
import { InlineCode } from '../components/code'
import Alert from '../components/alert'
import Search from '../components/search'

import siteMetadata from '../../meta/site.json'
import { nightly, legacy } from '../../meta/dynamicMeta'
import { remarkComponents } from '../remark'

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
                    But don&apos;t worry, your visited pages should be saved for you.
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
        this.state = { scope: { ...remarkComponents, ...props.scope } }
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
            <MDXProvider components={remarkComponents}>
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

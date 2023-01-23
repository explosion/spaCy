import React from 'react'
import PropTypes from 'prop-types'
import Helmet from 'react-helmet'
import { StaticQuery, graphql } from 'gatsby'

import socialImageDefault from '../images/social_default.jpg'
import socialImageApi from '../images/social_api.jpg'
import socialImageUniverse from '../images/social_universe.jpg'
import socialImageNightly from '../images/social_nightly.jpg'
import socialImageLegacy from '../images/social_legacy.jpg'

function getPageTitle(title, sitename, slogan, sectionTitle, nightly, legacy) {
    if (sectionTitle && title) {
        const suffix = nightly ? ' (nightly)' : legacy ? ' (legacy)' : ''
        return `${title} · ${sitename} ${sectionTitle}${suffix}`
    }
    if (title) {
        return `${title} · ${sitename}`
    }
    return `${sitename} · ${slogan}`
}

function getImage(section, nightly, legacy) {
    if (nightly) return socialImageNightly
    if (legacy) return socialImageLegacy
    if (section === 'api') return socialImageApi
    if (section === 'universe') return socialImageUniverse
    return socialImageDefault
}

export default function SEO({
    description,
    lang = 'en',
    title,
    section,
    sectionTitle,
    bodyClass,
    nightly,
    legacy,
}) {
    return (
        <StaticQuery
            query={query}
            render={data => {
                const siteMetadata = data.site.siteMetadata
                const metaDescription = description || siteMetadata.description
                const pageTitle = getPageTitle(
                    title,
                    siteMetadata.title,
                    siteMetadata.slogan,
                    sectionTitle,
                    nightly,
                    legacy
                )
                const socialImage = siteMetadata.siteUrl + getImage(section, nightly, legacy)
                const meta = [
                    {
                        name: 'description',
                        content: metaDescription,
                    },
                    {
                        property: 'og:title',
                        content: pageTitle,
                    },
                    {
                        property: 'og:description',
                        content: metaDescription,
                    },
                    {
                        property: 'og:type',
                        content: `website`,
                    },
                    {
                        property: 'og:site_name',
                        content: title,
                    },
                    {
                        property: 'og:image',
                        content: socialImage,
                    },
                    {
                        name: 'twitter:card',
                        content: 'summary_large_image',
                    },
                    {
                        name: 'twitter:image',
                        content: socialImage,
                    },
                    {
                        name: 'twitter:creator',
                        content: `@${siteMetadata.social.twitter}`,
                    },
                    {
                        name: 'twitter:site',
                        content: `@${siteMetadata.social.twitter}`,
                    },
                    {
                        name: 'twitter:title',
                        content: pageTitle,
                    },
                    {
                        name: 'twitter:description',
                        content: metaDescription,
                    },
                    {
                        name: 'docsearch:language',
                        content: lang,
                    },
                ]

                return (
                    <Helmet
                        defer={false}
                        htmlAttributes={{ lang }}
                        bodyAttributes={{ class: bodyClass }}
                        title={pageTitle}
                        meta={meta}
                    />
                )
            }}
        />
    )
}

SEO.propTypes = {
    description: PropTypes.string,
    lang: PropTypes.string,
    meta: PropTypes.array,
    keywords: PropTypes.arrayOf(PropTypes.string),
    title: PropTypes.string,
    section: PropTypes.string,
    bodyClass: PropTypes.string,
}

const query = graphql`
    query DefaultSEOQuery {
        site {
            siteMetadata {
                title
                description
                slogan
                siteUrl
                social {
                    twitter
                }
            }
        }
    }
`

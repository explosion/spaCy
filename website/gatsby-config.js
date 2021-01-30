const autoprefixer = require('autoprefixer')
const path = require('path')

// Markdown plugins
const wrapSectionPlugin = require('./src/plugins/remark-wrap-section.js')
const customAttrsPlugin = require('./src/plugins/remark-custom-attrs.js')
const codeBlocksPlugin = require('./src/plugins/remark-code-blocks.js')

// Import metadata
const site = require('./meta/site.json')
const logos = require('./meta/logos.json')
const sidebars = require('./meta/sidebars.json')
const models = require('./meta/languages.json')
const universe = require('./meta/universe.json')

const DEFAULT_TEMPLATE = path.resolve('./src/templates/index.js')
const legacy = site.legacy || !!+process.env.SPACY_LEGACY

module.exports = {
    siteMetadata: {
        ...site,
        legacy,
        ...logos,
        sidebars,
        ...models,
        universe,
    },

    plugins: [
        {
            resolve: `gatsby-plugin-sass`,
            options: {
                indentedSyntax: true,
                postCssPlugins: [autoprefixer()],
                cssLoaderOptions: {
                    localIdentName:
                        process.env.NODE_ENV == 'development'
                            ? '[name]-[local]-[hash:8]'
                            : '[hash:8]',
                },
            },
        },
        `gatsby-plugin-react-helmet`,
        {
            resolve: `gatsby-source-filesystem`,
            options: {
                name: `docs`,
                path: `${__dirname}/docs`,
            },
        },
        {
            resolve: `gatsby-source-filesystem`,
            options: {
                name: `pages`,
                path: `${__dirname}/src/pages`,
            },
        },
        {
            resolve: `gatsby-source-filesystem`,
            options: {
                name: `images`,
                path: `${__dirname}/src/images`,
            },
        },
        {
            resolve: `gatsby-source-filesystem`,
            options: {
                name: `docsImages`,
                path: `${__dirname}/docs/images`,
            },
        },
        {
            resolve: 'gatsby-plugin-react-svg',
            options: {
                rule: {
                    include: /src\/images\/(.*)\.svg/,
                },
            },
        },
        {
            resolve: `gatsby-mdx`,
            options: {
                root: __dirname,
                extensions: ['.md', '.mdx'],
                defaultLayouts: {
                    pages: DEFAULT_TEMPLATE,
                },
                mdPlugins: [customAttrsPlugin, wrapSectionPlugin, codeBlocksPlugin],
                gatsbyRemarkPlugins: [
                    {
                        resolve: `gatsby-remark-smartypants`,
                        options: {
                            backticks: false,
                            dashes: 'oldschool',
                        },
                    },
                    {
                        resolve: `gatsby-remark-images`,
                        options: {
                            maxWidth: 650,
                            linkImagesToOriginal: true,
                            sizeByPixelDensity: false,
                            showCaptions: true,
                            quality: 80,
                            withWebp: { quality: 80 },
                            wrapperStyle: { marginBottom: '20px' },
                        },
                    },
                    {
                        // NB: This need to run after gatsby-remark-images!
                        resolve: `gatsby-remark-unwrap-images`,
                    },
                    {
                        resolve: `gatsby-remark-copy-linked-files`,
                    },
                ],
            },
        },
        `gatsby-transformer-sharp`,
        `gatsby-plugin-sharp`,
        `gatsby-plugin-catch-links`,
        `gatsby-plugin-sitemap`,
        {
            resolve: `gatsby-plugin-manifest`,
            options: {
                name: site.title,
                short_name: site.title,
                start_url: `/`,
                background_color: site.theme,
                theme_color: site.theme,
                display: `minimal-ui`,
                icon: legacy ? `src/images/icon.png` : `src/images/icon_legacy.png`,
            },
        },
        {
            resolve: `gatsby-plugin-plausible`,
            options: {
                domain: site.domain,
            },
        },
        {
            resolve: 'gatsby-plugin-robots-txt',
            options: {
                host: site.siteUrl,
                sitemap: `${site.siteUrl}/sitemap.xml`,
                // If we're in a special state prevent indexing
                resolveEnv: () => (legacy ? 'development' : 'production'),
                env: {
                    production: {
                        policy: [{ userAgent: '*', allow: '/' }],
                    },
                    development: {
                        policy: [
                            { userAgent: '*', disallow: ['/'] },
                            { userAgent: 'Twitterbot', allow: '/' },
                        ],
                    },
                },
            },
        },
        `gatsby-plugin-offline`,
    ],
}

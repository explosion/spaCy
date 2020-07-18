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

module.exports = {
    siteMetadata: {
        ...site,
        ...logos,
        sidebars,
        ...models,
        universe,
    },

    plugins: [
        {
            resolve: `gatsby-plugin-svgr`,
            options: {
                svgo: false,
                svgoConfig: {
                    removeViewBox: false,
                },
            },
        },
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
                icon: `src/images/icon.png`,
            },
        },
        {
            resolve: `gatsby-plugin-google-analytics`,
            options: {
                trackingId: site.analytics,
                head: false,
                anonymize: true,
                respectDNT: true,
            },
        },
        {
            resolve: `gatsby-plugin-plausible`,
            options: {
                domain: site.domain,
            },
        },
        `gatsby-plugin-offline`,
    ],
}

const path = require('path')
const { createFilePath } = require('gatsby-source-filesystem')

const DEFAULT_TEMPLATE = path.resolve('./src/templates/index.js')
const BASE_PATH = 'docs'
const PAGE_EXTENSIONS = ['.md', '.mdx']

function replacePath(pagePath) {
    return pagePath === `/` ? pagePath : pagePath.replace(/\/$/, ``)
}

function getNodeTitle({ childMdx }) {
    const frontmatter = (childMdx || {}).frontmatter || {}
    return (frontmatter.title || '').replace("'", '’')
}

function findNode(pages, slug) {
    return slug ? pages.find(({ node }) => node.fields.slug === slug) : null
}

exports.createPages = ({ graphql, actions }) => {
    const { createPage } = actions

    return new Promise((resolve, reject) => {
        resolve(
            graphql(
                `
                    {
                        site {
                            siteMetadata {
                                sections {
                                    id
                                    title
                                    theme
                                }
                                languages {
                                    code
                                    name
                                    models
                                    example
                                    has_examples
                                }
                                universe {
                                    resources {
                                        id
                                        title
                                        slogan
                                    }
                                    categories {
                                        label
                                        items {
                                            id
                                            title
                                            description
                                        }
                                    }
                                }
                            }
                        }
                        allFile(filter: { ext: { in: [".md", ".mdx"] } }) {
                            edges {
                                node {
                                    base
                                    ext
                                    name
                                    relativeDirectory
                                    absolutePath
                                    childMdx {
                                        code {
                                            scope
                                        }
                                        frontmatter {
                                            title
                                            teaser
                                            source
                                            api_base_class
                                            api_string_name
                                            api_trainable
                                            tag
                                            new
                                            next
                                            search_exclude
                                            menu
                                            sidebar {
                                                label
                                                items {
                                                    text
                                                    url
                                                }
                                            }
                                            section
                                        }
                                    }
                                    fields {
                                        id
                                        slug
                                        fileName
                                    }
                                }
                            }
                        }
                    }
                `
            ).then(result => {
                if (result.errors) {
                    console.log(result.errors)
                    reject(result.errors)
                }

                const sectionData = result.data.site.siteMetadata.sections
                const sections = Object.assign({}, ...sectionData.map(s => ({ [s.id]: s })))

                /* Regular pages */

                const pages = result.data.allFile.edges
                pages.forEach(page => {
                    const { name } = path.parse(page.node.absolutePath)
                    if (!name.startsWith('_')) {
                        const mdx = page.node.childMdx || {}
                        const frontmatter = mdx.frontmatter || {}
                        const section = frontmatter.section || page.node.relativeDirectory
                        const sectionMeta = sections[section] || {}
                        const title = getNodeTitle(page.node)
                        const next = findNode(pages, frontmatter.next)
                        const baseClass = findNode(pages, frontmatter.api_base_class)
                        const apiDetails = {
                            stringName: frontmatter.api_string_name,
                            baseClass: baseClass
                                ? {
                                      title: getNodeTitle(baseClass.node),
                                      slug: frontmatter.api_base_class,
                                  }
                                : null,
                            trainable: frontmatter.api_trainable,
                        }
                        createPage({
                            path: replacePath(page.node.fields.slug),
                            component: DEFAULT_TEMPLATE,
                            context: {
                                id: page.node.id,
                                slug: page.node.fields.slug,
                                isIndex: page.node.fields.fileName === 'index',
                                title,
                                section,
                                sectionTitle: sectionMeta.title,
                                menu: frontmatter.menu || [],
                                teaser: frontmatter.teaser,
                                apiDetails,
                                source: frontmatter.source,
                                sidebar: frontmatter.sidebar,
                                tag: frontmatter.tag,
                                version: frontmatter.new,
                                theme: sectionMeta.theme,
                                searchExclude: frontmatter.search_exclude,
                                relativePath: page.node.relativePath,
                                next: next
                                    ? {
                                          title: getNodeTitle(next.node),
                                          slug: next.node.fields.slug,
                                      }
                                    : null,
                            },
                        })
                    }
                })

                /* Universe */

                const universeContext = {
                    section: 'universe',
                    sectionTitle: sections.universe.title,
                    theme: sections.universe.theme,
                }

                createPage({
                    path: '/universe',
                    component: DEFAULT_TEMPLATE,
                    context: {
                        slug: '/universe',
                        isIndex: true,
                        title: 'Overview',
                        ...universeContext,
                    },
                })

                const universe = result.data.site.siteMetadata.universe.resources
                universe.forEach(page => {
                    const slug = `/universe/project/${page.id}`

                    createPage({
                        path: slug,
                        component: DEFAULT_TEMPLATE,
                        context: {
                            id: page.id,
                            slug: slug,
                            isIndex: false,
                            title: page.title || page.id,
                            teaser: page.slogan,
                            data: { ...page, isProject: true },
                            ...universeContext,
                        },
                    })
                })

                const universeCategories = result.data.site.siteMetadata.universe.categories
                const categories = [].concat.apply([], universeCategories.map(cat => cat.items))
                categories.forEach(page => {
                    const slug = `/universe/category/${page.id}`

                    createPage({
                        path: slug,
                        component: DEFAULT_TEMPLATE,
                        context: {
                            id: page.id,
                            slug: slug,
                            isIndex: false,
                            title: page.title,
                            teaser: page.description,
                            data: { ...page, isCategory: true },
                            ...universeContext,
                        },
                    })
                })

                /* Models */

                const langs = result.data.site.siteMetadata.languages
                const modelLangs = langs.filter(({ models }) => models && models.length)
                modelLangs.forEach(({ code, name, models, example, has_examples }, i) => {
                    const slug = `/models/${code}`
                    const next = i < modelLangs.length - 1 ? modelLangs[i + 1] : null
                    createPage({
                        path: slug,
                        component: DEFAULT_TEMPLATE,
                        context: {
                            id: code,
                            slug: slug,
                            isIndex: false,
                            title: name,
                            section: 'models',
                            sectionTitle: sections.models.title,
                            theme: sections.models.theme,
                            next: next ? { title: next.name, slug: `/models/${next.code}` } : null,
                            meta: { models, example, hasExamples: has_examples },
                        },
                    })
                })
            })
        )
    })
}

exports.onCreateNode = ({ node, actions, getNode }) => {
    const { createNodeField } = actions
    if (PAGE_EXTENSIONS.includes(node.ext)) {
        const slug = createFilePath({ node, getNode, basePath: BASE_PATH, trailingSlash: false })
        const { name } = path.parse(node.absolutePath)
        createNodeField({ name: 'fileName', node, value: name })
        createNodeField({ name: 'slug', node, value: slug })
        createNodeField({ name: 'id', node, value: node.id })
    }
}

exports.onCreateWebpackConfig = ({ stage, loaders, actions }) => {
    // Support relative paths in MDX components
    actions.setWebpackConfig({
        resolve: {
            modules: [
                path.resolve(__dirname),
                path.resolve(__dirname, 'docs'),
                path.resolve(__dirname, 'src'),
                'node_modules',
            ],
        },
        module: {
            rules: [
                {
                    test: /\.(html|svg)$/,
                    use: 'raw-loader',
                },
            ],
        },
    })
    if (stage === 'build-javascript') {
        // Turn off source maps
        actions.setWebpackConfig({
            devtool: false,
        })
    }
}

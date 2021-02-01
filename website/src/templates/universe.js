import React from 'react'
import PropTypes from 'prop-types'
import { StaticQuery, graphql } from 'gatsby'

import Card from '../components/card'
import Link from '../components/link'
import Title from '../components/title'
import Grid from '../components/grid'
import Button from '../components/button'
import Icon from '../components/icon'
import CodeBlock, { InlineCode } from '../components/code'
import Aside from '../components/aside'
import Sidebar from '../components/sidebar'
import Section from '../components/section'
import Main from '../components/main'
import Footer from '../components/footer'
import { H3, H5, Label, InlineList } from '../components/typography'
import { YouTube, SoundCloud, Iframe } from '../components/embed'
import { github, markdownToReact } from '../components/util'

function getSlug(data) {
    if (data.isCategory) return `/universe/category/${data.id}`
    if (data.isProject) return `/universe/project/${data.id}`
    return `/universe`
}

function filterResources(resources, data) {
    const sorted = resources.sort((a, b) => a.id.localeCompare(b.id))
    if (!data || !data.isCategory) return sorted
    return sorted.filter(res => (res.category || []).includes(data.id))
}

const UniverseContent = ({ content = [], categories, theme, pageContext, mdxComponents }) => {
    const { data = {} } = pageContext
    const filteredResources = filterResources(content, data)
    const activeData = data ? content.find(({ id }) => id === data.id) : null
    const markdownComponents = { ...mdxComponents, code: InlineCode }
    const slug = getSlug(data)
    const isHome = !data.isCategory && !data.isProject

    const sidebar = [
        {
            label: 'Overview',
            items: [{ text: 'All Projects', url: '/universe' }],
        },
        ...categories.map(({ label, items }) => ({
            label,
            items: items.map(({ id, title }) => ({
                text: title,
                url: `/universe/category/${id}`,
            })),
        })),
    ]

    return (
        <>
            <Sidebar items={sidebar} slug={slug} />
            <Main section="universe" theme={theme} sidebar asides wrapContent footer={<Footer />}>
                {activeData ? (
                    <Project data={activeData} components={markdownComponents} />
                ) : (
                    <Section>
                        {isHome ? (
                            <Title
                                title="Universe"
                                teaser="This section collects the many great resources developed with or for spaCy. It includes standalone packages, plugins, extensions, educational materials, operational utilities and bindings for other languages."
                            />
                        ) : (
                            <Title
                                title={data.title}
                                teaser={data.description}
                                tag={String(filteredResources.length)}
                            />
                        )}
                        <Grid
                            cols={data && data.isCategory && data.id === 'books' ? 3 : 2}
                            className="search-exclude"
                        >
                            {filteredResources.map(
                                ({ id, type, title, slogan, thumb, cover, youtube }) => {
                                    if (isHome && type === 'education') {
                                        return null
                                    }
                                    const url = `/universe/project/${id}`
                                    const header = youtube && (
                                        <img
                                            src={`https://img.youtube.com/vi/${youtube}/0.jpg`}
                                            alt=""
                                            style={{
                                                clipPath: 'inset(12.9% 0)',
                                                marginBottom: 'calc(-12.9% + 1rem)',
                                            }}
                                        />
                                    )
                                    return cover ? (
                                        <p key={id}>
                                            <Link key={id} to={url} hidden>
                                                <img src={cover} alt={title || id} />
                                            </Link>
                                        </p>
                                    ) : data.id === 'videos' ? (
                                        <div>
                                            <Link key={id} to={url} hidden>
                                                {header}
                                                <H5>{title}</H5>
                                            </Link>
                                        </div>
                                    ) : (
                                        <Card
                                            key={id}
                                            title={title || id}
                                            image={thumb}
                                            to={url}
                                            header={header}
                                        >
                                            {slogan}
                                        </Card>
                                    )
                                }
                            )}
                        </Grid>
                    </Section>
                )}
                <section className="search-exclude">
                    <H3>Submit your project</H3>
                    <p>
                        If you have a project that you want the spaCy community to make use of, you
                        can suggest it by submitting a pull request to the spaCy website repository.
                        The Universe database is open-source and collected in a simple JSON file.
                        For more details on the formats and available fields, see the documentation.
                        Looking for inspiration your own spaCy plugin or extension? Check out the
                        <Link to={github() + '/labels/project%20idea'} hideIcon ws>
                            <InlineCode>project idea</InlineCode>
                        </Link>
                        label on the issue tracker.
                    </p>

                    <InlineList>
                        <Button variant="primary" to={github('website/UNIVERSE.md')}>
                            Read the docs
                        </Button>
                        <Button icon="code" to={github('website/meta/universe.json')}>
                            JSON source
                        </Button>
                    </InlineList>
                </section>
            </Main>
        </>
    )
}

UniverseContent.propTypes = {
    content: PropTypes.arrayOf(PropTypes.object),
    categories: PropTypes.arrayOf(
        PropTypes.shape({
            label: PropTypes.string.isRequired,
            items: PropTypes.arrayOf(
                PropTypes.shape({
                    id: PropTypes.string.isRequired,
                    title: PropTypes.string.isRequired,
                    description: PropTypes.string.isRequired,
                })
            ).isRequired,
        })
    ).isRequired,
    theme: PropTypes.string,
    location: PropTypes.object.isRequired,
    mdxComponents: PropTypes.object,
}

const Project = ({ data, components }) => (
    <>
        <Title title={data.title || data.id} teaser={data.slogan} image={data.thumb}>
            {data.github && (
                <p>
                    <Link to={`https://github.com/${data.github}`} hidden>
                        {[
                            `release/${data.github}/all.svg?style=flat-square`,
                            `license/${data.github}.svg?style=flat-square`,
                            `stars/${data.github}.svg?style=social&label=Stars`,
                        ].map((url, i) => (
                            <img
                                style={{ borderRadius: '1em', marginRight: '0.5rem' }}
                                key={i}
                                src={`https://img.shields.io/github/${url}`}
                                alt=""
                            />
                        ))}
                    </Link>
                </p>
            )}
        </Title>
        {data.pip && (
            <Aside title="Installation">
                <CodeBlock lang="bash" prompt="$">
                    pip install {data.pip}
                </CodeBlock>
            </Aside>
        )}
        {data.cran && (
            <Aside title="Installation">
                <CodeBlock lang="r">install.packages("{data.cran}")</CodeBlock>
            </Aside>
        )}

        {data.cover && (
            <p>
                <img src={data.cover} alt={data.title} width={250} style={{ maxWidth: '50%' }} />
            </p>
        )}

        <Section>
            {data.youtube && <YouTube id={data.youtube} />}
            {data.soundcloud && <SoundCloud id={data.soundcloud} title={data.title} />}
            {data.iframe && (
                <Iframe
                    src={data.iframe}
                    title={data.title}
                    width="100%"
                    height={data.iframe_height}
                />
            )}

            {data.description && <section>{markdownToReact(data.description, components)}</section>}

            {data.code_example && (
                <CodeBlock title="Example" lang={data.code_language || 'python'}>
                    {data.code_example.join('\n')}
                </CodeBlock>
            )}

            {data.image && (
                <p>
                    <img src={data.image} style={{ maxWidth: '100%' }} alt="" />
                </p>
            )}

            {data.url && (
                <Button variant="primary" to={data.url}>
                    View more
                </Button>
            )}
        </Section>

        <Section>
            <Grid cols={2}>
                <div>
                    <Label>Author info</Label>
                    <InlineList gutterBottom={false}>
                        <span>{data.author}</span>
                        <span>
                            {data.author_links && data.author_links.twitter && (
                                <Link
                                    to={`https://twitter.com/${data.author_links.twitter}`}
                                    hidden
                                    ws
                                >
                                    <Icon width={18} name="twitter" inline />
                                </Link>
                            )}
                            {data.author_links && data.author_links.github && (
                                <Link
                                    to={`https://github.com/${data.author_links.github}`}
                                    hidden
                                    ws
                                >
                                    <Icon width={18} name="github" inline />
                                </Link>
                            )}
                            {data.author_links && data.author_links.website && (
                                <Link to={data.author_links.website} hidden ws>
                                    <Icon width={18} name="website" inline />
                                </Link>
                            )}
                        </span>
                    </InlineList>
                </div>
                {data.github && (
                    <p style={{ marginBottom: 0 }}>
                        <Label>GitHub</Label>
                        <Link to={`https://github.com/${data.github}`}>
                            <InlineCode wrap>{data.github}</InlineCode>
                        </Link>
                    </p>
                )}
            </Grid>
            {data.category && (
                <p style={{ marginBottom: 0 }}>
                    <Label>Categories</Label>
                    {data.category.map(cat => (
                        <Link to={`/universe/category/${cat}`} key={cat} ws>
                            <InlineCode>{cat}</InlineCode>
                        </Link>
                    ))}
                </p>
            )}
        </Section>
    </>
)

const Universe = ({ pageContext, location, mdxComponents }) => (
    <StaticQuery
        query={query}
        render={data => {
            const { universe, nightly, legacy } = data.site.siteMetadata
            const theme = nightly ? 'nightly' : legacy ? 'legacy' : pageContext.theme
            return (
                <UniverseContent
                    content={universe.resources}
                    categories={universe.categories}
                    pageContext={pageContext}
                    location={location}
                    mdxComponents={mdxComponents}
                    theme={theme}
                />
            )
        }}
    />
)

export default Universe

const query = graphql`
    query UniverseQuery {
        site {
            siteMetadata {
                nightly
                legacy
                universe {
                    resources {
                        type
                        id
                        title
                        slogan
                        url
                        github
                        description
                        pip
                        cran
                        category
                        thumb
                        image
                        cover
                        code_example
                        code_language
                        youtube
                        soundcloud
                        iframe
                        iframe_height
                        author
                        author_links {
                            twitter
                            github
                            website
                        }
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
    }
`

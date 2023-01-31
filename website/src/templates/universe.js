import React from 'react'
import PropTypes from 'prop-types'

import Card from '../components/card'
import Link from '../components/link'
import Title from '../components/title'
import Grid from '../components/grid'
import Button from '../components/button'
import Icon from '../components/icon'
import Tag from '../components/tag'
import { InlineCode } from '../components/inlineCode'
import CodeBlock from '../components/codeBlock'
import Aside from '../components/aside'
import Sidebar from '../components/sidebar'
import Section, { Hr } from '../components/section'
import Main from '../components/main'
import Footer from '../components/footer'
import { H3, H5, Label, InlineList } from '../components/typography'
import { YouTube, SoundCloud, Iframe } from '../components/embed'
import { github } from '../components/util'
import MarkdownToReact from '../components/markdownToReactDynamic'

import { nightly, legacy } from '../../meta/dynamicMeta.mjs'
import universe from '../../meta/universe.json'
import Image from 'next/image'

function filterResources(resources, data) {
    const sorted = resources.sort((a, b) => a.id.localeCompare(b.id))
    if (!data || !data.isCategory) return sorted
    return sorted.filter((res) => (res.category || []).includes(data.id))
}

const UniverseContent = ({ content = [], categories, theme, pageContext, mdxComponents }) => {
    const { data = {} } = pageContext
    const filteredResources = filterResources(content, data)
    const activeData = data ? content.find(({ id }) => id === data.id) : null
    const markdownComponents = { ...mdxComponents, code: InlineCode }
    const slug = pageContext.slug
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
                                        <Image
                                            src={`https://img.youtube.com/vi/${youtube}/0.jpg`}
                                            alt={title}
                                            width="480"
                                            height="360"
                                            style={{
                                                clipPath: 'inset(12.9% 0)',
                                                marginBottom: 'calc(-12.9% + 1rem)',
                                            }}
                                        />
                                    )
                                    return cover ? (
                                        <p key={id}>
                                            <Link key={id} to={url} noLinkLayout>
                                                {/* eslint-disable-next-line @next/next/no-img-element */}
                                                <img src={cover} alt={title || id} />
                                            </Link>
                                        </p>
                                    ) : data.id === 'videos' ? (
                                        <div>
                                            <Link key={id} to={url} noLinkLayout>
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
                    <H3>Found a mistake or something isn&apos;t working?</H3>
                    <p>
                        If you&apos;ve come across a universe project that isn&apos;t working or is
                        incompatible with the reported spaCy version, let us know by{' '}
                        <Link to="https://github.com/explosion/spaCy/discussions/new">
                            opening a discussion thread
                        </Link>
                        .
                    </p>
                </section>
                <Hr />
                <section className="search-exclude">
                    <H3>Submit your project</H3>
                    <p>
                        If you have a project that you want the spaCy community to make use of, you
                        can suggest it by submitting a pull request to the spaCy website repository.
                        The Universe database is open-source and collected in a simple JSON file.
                        For more details on the formats and available fields, see the documentation.
                        Looking for inspiration your own spaCy plugin or extension? Check out the
                        <Link
                            to={
                                'https://github.com/explosion/spaCy/discussions/categories/new-features-project-ideas/'
                            }
                            hideIcon
                            ws
                        >
                            project idea
                        </Link>
                        section in Discussions.
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

const SpaCyVersion = ({ version }) => {
    const versions = !Array.isArray(version) ? [version] : version
    return versions.map((v, i) => (
        <>
            <Tag tooltip={`This project is compatible with spaCy v${v}`}>spaCy v{v}</Tag>{' '}
        </>
    ))
}

const ImageGitHub = ({ url, isRounded, title }) => (
    // eslint-disable-next-line @next/next/no-img-element
    <img
        style={{
            borderRadius: isRounded ? '1em' : 0,
            marginRight: '0.5rem',
            verticalAlign: 'middle',
        }}
        src={`https://img.shields.io/github/${url}`}
        alt={`${title} on GitHub`}
    />
)

const Project = ({ data, components }) => (
    <>
        <Title title={data.title || data.id} teaser={data.slogan} image={data.thumb}>
            {(data.github || data.spacy_version) && (
                <p>
                    {data.spacy_version && <SpaCyVersion version={data.spacy_version} />}
                    {data.github && (
                        <Link to={`https://github.com/${data.github}`} noLinkLayout>
                            <ImageGitHub
                                title={data.title || data.id}
                                url={`release/${data.github}/all.svg?style=flat-square`}
                                isRounded
                            />
                            <ImageGitHub
                                title={data.title || data.id}
                                url={`license/${data.github}.svg?style=flat-square`}
                                isRounded
                            />
                            <ImageGitHub
                                title={data.title || data.id}
                                url={`stars/${data.github}.svg?style=social&label=Stars`}
                            />
                        </Link>
                    )}
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
                <CodeBlock lang="r">install.packages(&quot;{data.cran}&quot;)</CodeBlock>
            </Aside>
        )}

        {data.cover && (
            <p>
                {/* eslint-disable-next-line @next/next/no-img-element */}
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

            {data.description && (
                <section>
                    <MarkdownToReact markdown={data.description} />
                </section>
            )}

            {data.code_example && (
                <CodeBlock title="Example" lang={data.code_language || 'python'}>
                    {data.code_example.join('\n')}
                </CodeBlock>
            )}

            {data.image && (
                <p>
                    {/* eslint-disable-next-line @next/next/no-img-element */}
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
                                    noLinkLayout
                                    ws
                                >
                                    <Icon width={18} name="twitter" inline />
                                </Link>
                            )}
                            {data.author_links && data.author_links.github && (
                                <Link
                                    to={`https://github.com/${data.author_links.github}`}
                                    noLinkLayout
                                    ws
                                >
                                    <Icon width={18} name="github" inline />
                                </Link>
                            )}
                            {data.author_links && data.author_links.website && (
                                <Link to={data.author_links.website} noLinkLayout ws>
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
                    {data.category.map((cat) => (
                        <Link to={`/universe/category/${cat}`} key={cat} ws>
                            <InlineCode>{cat}</InlineCode>
                        </Link>
                    ))}
                </p>
            )}
        </Section>
    </>
)

const Universe = ({ pageContext, location, mdxComponents }) => {
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
}

export default Universe

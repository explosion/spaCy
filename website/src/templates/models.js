import React, { useEffect, useState, useMemo, Fragment } from 'react'
import { StaticQuery, graphql } from 'gatsby'
import { window } from 'browser-monads'

import Title from '../components/title'
import Section from '../components/section'
import Button from '../components/button'
import Aside from '../components/aside'
import CodeBlock, { InlineCode } from '../components/code'
import { Table, Tr, Td, Th } from '../components/table'
import Tag from '../components/tag'
import { H2, Label } from '../components/typography'
import Icon from '../components/icon'
import Link from '../components/link'
import Grid from '../components/grid'
import Infobox from '../components/infobox'
import Accordion from '../components/accordion'
import { join, arrayToObj, abbrNum, markdownToReact } from '../components/util'
import { isString, isEmptyObj } from '../components/util'

const MODEL_META = {
    core: 'Vocabulary, syntax, entities, vectors',
    core_sm: 'Vocabulary, syntax, entities',
    dep: 'Vocabulary, syntax',
    ent: 'Named entities',
    pytt: 'PyTorch Transformers',
    trf: 'Transformers',
    vectors: 'Word vectors',
    web: 'written text (blogs, news, comments)',
    news: 'written text (news, media)',
    wiki: 'Wikipedia',
    uas: 'Unlabelled dependencies',
    las: 'Labelled dependencies',
    tags_acc: 'Part-of-speech tags (fine grained tags, Token.tag)',
    ents_f: 'Entities (F-score)',
    ents_p: 'Entities (precision)',
    ents_r: 'Entities (recall)',
    cpu: 'words per second on CPU',
    gpu: 'words per second on GPU',
    pipeline: 'Processing pipeline components in order',
    sources: 'Sources of training data',
    vecs:
        'Word vectors included in the model. Models that only support context vectors compute similarity via the tensors shared with the pipeline.',
    benchmark_parser: 'Syntax accuracy',
    benchmark_ner: 'NER accuracy',
    benchmark_speed: 'Speed',
    compat: 'Latest compatible model version for your spaCy installation',
}

const LABEL_SCHEME_META = {
    tagger: 'Part-of-speech tags via Token.tag_',
    parser: 'Dependency labels via Token.dep_',
    ner: 'Named entity labels',
}

const MARKDOWN_COMPONENTS = {
    code: InlineCode,
}

function getModelComponents(name) {
    const [lang, type, genre, size] = name.split('_')
    return { lang, type, genre, size }
}

function isStableVersion(v) {
    return !v.includes('a') && !v.includes('b') && !v.includes('dev') && !v.includes('rc')
}

function getLatestVersion(modelId, compatibility) {
    for (let [version, models] of Object.entries(compatibility)) {
        if (isStableVersion(version) && models[modelId]) {
            return models[modelId][0]
        }
    }
}

function formatVectors(data) {
    if (!data) return 'n/a'
    if (Object.values(data).every(n => n === 0)) return 'context vectors only'
    const { keys, vectors, width } = data
    return `${abbrNum(keys)} keys, ${abbrNum(vectors)} unique vectors (${width} dimensions)`
}

function formatAccuracy(data) {
    if (!data) return null
    const labels = {
        las: 'LAS',
        uas: 'UAS',
        tags_acc: 'TAG',
        ents_f: 'NER F',
        ents_p: 'NER P',
        ents_r: 'NER R',
    }
    const isSyntax = key => ['tags_acc', 'las', 'uas'].includes(key)
    const isNer = key => key.startsWith('ents_')
    return Object.keys(data)
        .filter(key => labels[key])
        .map(key => ({
            label: labels[key],
            value: data[key].toFixed(2),
            help: MODEL_META[key],
            type: isNer(key) ? 'ner' : isSyntax(key) ? 'syntax' : null,
        }))
}

function formatModelMeta(data) {
    return {
        fullName: `${data.lang}_${data.name}-${data.version}`,
        version: data.version,
        sizeFull: data.size,
        pipeline: data.pipeline,
        notes: data.notes,
        description: data.description,
        sources: data.sources,
        author: data.author,
        url: data.url,
        license: data.license,
        labels: isEmptyObj(data.labels) ? null : data.labels,
        vectors: formatVectors(data.vectors),
        accuracy: formatAccuracy(data.accuracy),
    }
}

function formatSources(data = []) {
    const sources = data.map(s => (isString(s) ? { name: s } : s))
    return sources.map(({ name, url, author }, i) => (
        <Fragment key={i}>
            {i > 0 && <br />}
            {name && url ? <Link to={url}>{name}</Link> : name}
            {author && ` (${author})`}
        </Fragment>
    ))
}

const Help = ({ children }) => (
    <span data-tooltip={children}>
        <Icon name="help2" width={16} variant="subtle" inline />
    </span>
)

const Model = ({ name, langId, langName, baseUrl, repo, compatibility, hasExamples, licenses }) => {
    const [initialized, setInitialized] = useState(false)
    const [isError, setIsError] = useState(true)
    const [meta, setMeta] = useState({})
    const { type, genre, size } = getModelComponents(name)
    const version = useMemo(() => getLatestVersion(name, compatibility), [name, compatibility])

    useEffect(() => {
        window.dispatchEvent(new Event('resize')) // scroll position for progress
        if (!initialized && version) {
            setIsError(false)
            fetch(`${baseUrl}/meta/${name}-${version}.json`)
                .then(res => res.json())
                .then(json => {
                    setMeta(formatModelMeta(json))
                })
                .catch(err => {
                    setIsError(true)
                    console.error(err)
                })
            setInitialized(true)
        }
    }, [initialized, version, baseUrl, name])

    const releaseTag = meta.fullName ? `/tag/${meta.fullName}` : ''
    const releaseUrl = `https://github.com/${repo}/releases/${releaseTag}`
    const pipeline =
        meta.pipeline && join(meta.pipeline.map(p => <InlineCode key={p}>{p}</InlineCode>))
    const sources = formatSources(meta.sources)
    const author = !meta.url ? meta.author : <Link to={meta.url}>{meta.author}</Link>
    const licenseUrl = licenses[meta.license] ? licenses[meta.license].url : null
    const license = licenseUrl ? <Link to={licenseUrl}>{meta.license}</Link> : meta.license
    const hasInteractiveCode = size === 'sm' && hasExamples && !isError
    const labels = meta.labels

    const rows = [
        { label: 'Language', tag: langId, content: langName },
        { label: 'Type', tag: type, content: MODEL_META[type] },
        { label: 'Genre', tag: genre, content: MODEL_META[genre] },
        { label: 'Size', tag: size, content: meta.sizeFull },
        { label: 'Pipeline', content: pipeline, help: MODEL_META.pipeline },
        { label: 'Vectors', content: meta.vectors, help: MODEL_META.vecs },
        { label: 'Sources', content: sources, help: MODEL_META.sources },
        { label: 'Author', content: author },
        { label: 'License', content: license },
    ]
    const accuracy = [
        {
            label: 'Syntax Accuracy',
            items: meta.accuracy ? meta.accuracy.filter(a => a.type === 'syntax') : null,
        },
        {
            label: 'NER Accuracy',
            items: meta.accuracy ? meta.accuracy.filter(a => a.type === 'ner') : null,
        },
    ]

    const error = (
        <Infobox title="Unable to load model details from GitHub" variant="danger">
            <p>
                To find out more about this model, see the overview of the{' '}
                <Link to={`https://github.com/${repo}/releases`} ws hideIcon>
                    latest model releases.
                </Link>
            </p>
        </Infobox>
    )

    return (
        <Section id={name}>
            <H2
                id={name}
                action={
                    <>
                        <Button to={releaseUrl}>Release Details</Button>
                        {version && (
                            <div>
                                Latest: <InlineCode>{version}</InlineCode>
                            </div>
                        )}
                    </>
                }
            >
                {name}
            </H2>
            <Aside title="Installation">
                <CodeBlock lang="bash" prompt="$">
                    python -m spacy download {name}
                </CodeBlock>
            </Aside>
            {meta.description && markdownToReact(meta.description, MARKDOWN_COMPONENTS)}
            {isError && error}
            <Table>
                <tbody>
                    {rows.map(({ label, tag, help, content }, i) =>
                        !tag && !content ? null : (
                            <Tr key={i}>
                                <Td nowrap>
                                    <Label>
                                        {`${label} `}
                                        {help && <Help>{help}</Help>}
                                    </Label>
                                </Td>
                                <Td>
                                    {tag && <Tag spaced>{tag}</Tag>}
                                    {content}
                                </Td>
                            </Tr>
                        )
                    )}
                </tbody>
            </Table>
            <Grid cols={2} gutterBottom={hasInteractiveCode || !!labels}>
                {accuracy &&
                    accuracy.map(({ label, items }, i) =>
                        !items ? null : (
                            <Table fixed key={i}>
                                <thead>
                                    <Tr>
                                        <Th colSpan={2}>{label}</Th>
                                    </Tr>
                                </thead>
                                <tbody>
                                    {items.map((item, i) => (
                                        <Tr key={i}>
                                            <Td>
                                                <Label>
                                                    {item.label}{' '}
                                                    {item.help && <Help>{item.help}</Help>}
                                                </Label>
                                            </Td>
                                            <Td num>{item.value}</Td>
                                        </Tr>
                                    ))}
                                </tbody>
                            </Table>
                        )
                    )}
            </Grid>
            {meta.notes && markdownToReact(meta.notes, MARKDOWN_COMPONENTS)}
            {hasInteractiveCode && (
                <CodeBlock title="Try out the model" lang="python" executable={true}>
                    {[
                        `import spacy`,
                        `from spacy.lang.${langId}.examples import sentences `,
                        ``,
                        `nlp = spacy.load('${name}')`,
                        `doc = nlp(sentences[0])`,
                        `print(doc.text)`,
                        `for token in doc:`,
                        `    print(token.text, token.pos_, token.dep_)`,
                    ].join('\n')}
                </CodeBlock>
            )}
            {labels && (
                <Accordion id={`${name}-labels`} title="Label Scheme">
                    <p>
                        The statistical components included in this model package assign the
                        following labels. The labels are specific to the corpus that the model was
                        trained on. To see the description of a label, you can use{' '}
                        <Link to="/api/top-level#spacy.explain">
                            <InlineCode>spacy.explain</InlineCode>
                        </Link>
                        .
                    </p>
                    <Table fixed>
                        <tbody>
                            {Object.keys(labels).map(pipe => {
                                const labelNames = labels[pipe] || []
                                const help = LABEL_SCHEME_META[pipe]
                                return (
                                    <Tr key={pipe} evenodd={false} key={pipe}>
                                        <Td style={{ width: '20%' }}>
                                            <Label>
                                                {pipe} {help && <Help>{help}</Help>}
                                            </Label>
                                        </Td>
                                        <Td>
                                            {labelNames.map((label, i) => (
                                                <Fragment key={i}>
                                                    {i > 0 && ', '}
                                                    <InlineCode wrap key={label}>
                                                        {label}
                                                    </InlineCode>
                                                </Fragment>
                                            ))}
                                        </Td>
                                    </Tr>
                                )
                            })}
                        </tbody>
                    </Table>
                </Accordion>
            )}
        </Section>
    )
}

const Models = ({ pageContext, repo, children }) => {
    const [initialized, setInitialized] = useState(false)
    const [compatibility, setCompatibility] = useState({})
    const { id, title, meta } = pageContext
    const { models, isStarters } = meta
    const baseUrl = `https://raw.githubusercontent.com/${repo}/master`

    useEffect(() => {
        window.dispatchEvent(new Event('resize')) // scroll position for progress
        if (!initialized) {
            fetch(`${baseUrl}/compatibility.json`)
                .then(res => res.json())
                .then(({ spacy }) => setCompatibility(spacy))
                .catch(err => console.error(err))
            setInitialized(true)
        }
    }, [initialized, baseUrl])

    const modelTitle = title
    const modelTeaser = `Available pretrained statistical models for ${title}`

    const starterTitle = `${title} starters`
    const starterTeaser = `Available transfer learning starter packs for ${title}`

    return (
        <>
            <Title
                title={isStarters ? starterTitle : modelTitle}
                teaser={isStarters ? starterTeaser : modelTeaser}
            />
            {isStarters && (
                <Section>
                    <p>
                        Starter packs are pretrained weights you can initialize your models with to
                        achieve better accuracy. They can include word vectors (which will be used
                        as features during training) or other pretrained representations like BERT.
                    </p>
                </Section>
            )}
            <StaticQuery
                query={query}
                render={({ site }) =>
                    models.map(modelName => (
                        <Model
                            key={modelName}
                            name={modelName}
                            langId={id}
                            langName={title}
                            compatibility={compatibility}
                            baseUrl={baseUrl}
                            repo={repo}
                            licenses={arrayToObj(site.siteMetadata.licenses, 'id')}
                        />
                    ))
                }
            />

            {children}
        </>
    )
}

export default Models

const query = graphql`
    query ModelsQuery {
        site {
            siteMetadata {
                licenses {
                    id
                    url
                }
            }
        }
    }
`

import React, { useEffect, useState, useMemo } from 'react'
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
import { join, arrayToObj, abbrNum } from '../components/util'

const MODEL_META = {
    core: 'Vocabulary, syntax, entities, vectors',
    core_sm: 'Vocabulary, syntax, entities',
    dep: 'Vocabulary, syntax',
    ent: 'Named entities',
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
    const labels = { tags_acc: 'POS', ents_f: 'NER F', ents_p: 'NER P', ents_r: 'NER R' }
    const isSyntax = key => ['tags_acc', 'las', 'uas'].includes(key)
    const isNer = key => key.startsWith('ents_')
    return Object.keys(data).map(key => ({
        label: labels[key] || key.toUpperCase(),
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
        vectors: formatVectors(data.vectors),
        accuracy: formatAccuracy(data.accuracy),
    }
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
    const sources = meta.sources && join(meta.sources)
    const author = !meta.url ? meta.author : <Link to={meta.url}>{meta.author}</Link>
    const licenseUrl = licenses[meta.license] ? licenses[meta.license].url : null
    const license = licenseUrl ? <Link to={licenseUrl}>{meta.license}</Link> : meta.license
    const hasInteractiveCode = size === 'sm' && hasExamples && !isError

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
            {meta.description && <p>{meta.description}</p>}

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
            <Grid cols={2} gutterBottom={hasInteractiveCode}>
                {accuracy &&
                    accuracy.map(({ label, items }, i) =>
                        !items ? null : (
                            <Table key={i}>
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
            {meta.notes && <p>{meta.notes}</p>}
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
        </Section>
    )
}

const Models = ({ pageContext, repo, children }) => {
    const [initialized, setInitialized] = useState(false)
    const [compatibility, setCompatibility] = useState({})
    const { id, title, meta } = pageContext
    const { models } = meta
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

    return (
        <>
            <Title title={title} teaser={`Available pre-trained statistical models for ${title}`} />
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
                            hasExamples={meta.hasExamples}
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

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
import Link, { OptionalLink } from '../components/link'
import Infobox from '../components/infobox'
import Accordion from '../components/accordion'
import { join, arrayToObj, abbrNum, markdownToReact } from '../components/util'
import { isString, isEmptyObj } from '../components/util'

const COMPONENT_LINKS = {
    tok2vec: '/api/tok2vec',
    transformer: '/api/transformer',
    tagger: '/api/tagger',
    parser: '/api/dependencyparser',
    ner: '/api/entityrecognizer',
    lemmatizer: '/api/lemmatizer',
    attribute_ruler: '/api/attributeruler',
    senter: '/api/sentencerecognizer',
    morphologizer: '/api/morphologizer',
}

const MODEL_META = {
    core: 'Vocabulary, syntax, entities, vectors',
    core_no_vectors: 'Vocabulary, syntax, entities',
    dep: 'Vocabulary, syntax',
    ent: 'Named entities',
    sent: 'Sentence boundaries',
    pytt: 'PyTorch Transformers',
    trf: 'Transformers',
    vectors: 'Word vectors',
    web: 'written text (blogs, news, comments)',
    news: 'written text (news, media)',
    wiki: 'Wikipedia',
    uas: 'Unlabeled dependencies',
    las: 'Labeled dependencies',
    dep_uas: 'Unlabeled dependencies',
    dep_las: 'Labeled dependencies',
    token_acc: 'Tokenization',
    tok: 'Tokenization',
    lemma: 'Lemmatization',
    morph: 'Morphological analysis',
    lemma_acc: 'Lemmatization',
    morph_acc: 'Morphological analysis',
    tags_acc: 'Part-of-speech tags (fine grained tags, Token.tag)',
    tag_acc: 'Part-of-speech tags (fine grained tags, Token.tag)',
    tag: 'Part-of-speech tags (fine grained tags, Token.tag)',
    pos: 'Part-of-speech tags (coarse grained tags, Token.pos)',
    pos_acc: 'Part-of-speech tags (coarse grained tags, Token.pos)',
    ents_f: 'Named entities (F-score)',
    ents_p: 'Named entities (precision)',
    ents_r: 'Named entities (recall)',
    ner_f: 'Named entities (F-score)',
    ner_p: 'Named entities (precision)',
    ner_r: 'Named entities (recall)',
    sents_f: 'Sentence segmentation (F-score)',
    sents_p: 'Sentence segmentation (precision)',
    sents_r: 'Sentence segmentation (recall)',
    cpu: 'words per second on CPU',
    gpu: 'words per second on GPU',
    pipeline: 'Active processing pipeline components in order',
    components: 'All processing pipeline components (including disabled components)',
    sources: 'Sources of training data',
    vecs:
        'Word vectors included in the package. Packages that only support context vectors compute similarity via the tensors shared with the pipeline.',
    benchmark_parser: 'Syntax accuracy',
    benchmark_ner: 'NER accuracy',
    benchmark_speed: 'Speed',
    compat: 'Latest compatible package version for your spaCy installation',
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

function getLatestVersion(modelId, compatibility, prereleases) {
    for (let [version, models] of Object.entries(compatibility)) {
        if (isStableVersion(version) && models[modelId]) {
            const modelVersions = models[modelId]
            for (let modelVersion of modelVersions) {
                if (isStableVersion(modelVersion) || prereleases) {
                    return modelVersion
                }
            }
        }
    }
}

function formatVectors(data) {
    if (!data) return 'n/a'
    if (Object.values(data).every(n => n === 0)) return 'context vectors only'
    const { keys, vectors, width } = data
    return `${abbrNum(keys)} keys, ${abbrNum(vectors)} unique vectors (${width} dimensions)`
}

function formatAccuracy(data, lang) {
    const exclude = (lang !== "ja") ? ['speed'] : ['speed', 'morph_acc']
    if (!data) return []
    return Object.keys(data)
        .map(label => {
            const value = data[label]
            return isNaN(value) || exclude.includes(label)
                ? null
                : {
                      label,
                      value: value.toFixed(2),
                      help: MODEL_META[label],
                  }
        })
        .filter(item => item)
}

function formatModelMeta(data) {
    return {
        fullName: `${data.lang}_${data.name}-${data.version}`,
        version: data.version,
        sizeFull: data.size,
        pipeline: data.pipeline,
        components: data.components,
        notes: data.notes,
        description: data.description,
        sources: data.sources,
        author: data.author,
        url: data.url,
        license: data.license,
        labels: isEmptyObj(data.labels) ? null : data.labels,
        vectors: formatVectors(data.vectors),
        accuracy: formatAccuracy(data.performance, data.lang),
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

function linkComponents(components = []) {
    return join(
        components.map(c => (
            <Fragment key={c}>
                <OptionalLink to={COMPONENT_LINKS[c]} hideIcon>
                    <InlineCode>{c}</InlineCode>
                </OptionalLink>
            </Fragment>
        ))
    )
}

const Help = ({ children }) => (
    <span data-tooltip={children}>
        <Icon name="help2" width={16} variant="subtle" inline />
    </span>
)

const Model = ({
    name,
    langId,
    langName,
    baseUrl,
    repo,
    compatibility,
    hasExamples,
    licenses,
    prereleases,
}) => {
    const [initialized, setInitialized] = useState(false)
    const [isError, setIsError] = useState(true)
    const [meta, setMeta] = useState({})
    const { type, genre, size } = getModelComponents(name)
    const display_type = type === 'core' && (size === 'sm' || size === 'trf') ? 'core_no_vectors' : type
    const version = useMemo(() => getLatestVersion(name, compatibility, prereleases), [
        name,
        compatibility,
        prereleases,
    ])

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

    const releaseTag = meta.fullName ? `tag/${meta.fullName}` : ''
    const releaseUrl = `https://github.com/${repo}/releases/${releaseTag}`
    const pipeline = linkComponents(meta.pipeline)
    const components = linkComponents(meta.components)
    const sources = formatSources(meta.sources)
    const author = !meta.url ? meta.author : <Link to={meta.url}>{meta.author}</Link>
    const licenseUrl = licenses[meta.license] ? licenses[meta.license].url : null
    const license = licenseUrl ? <Link to={licenseUrl}>{meta.license}</Link> : meta.license
    const hasInteractiveCode = size === 'sm' && hasExamples && !isError
    const labels = meta.labels

    const rows = [
        { label: 'Language', tag: langId, content: langName },
        { label: 'Type', tag: type, content: MODEL_META[display_type] },
        { label: 'Genre', tag: genre, content: MODEL_META[genre] },
        { label: 'Size', tag: size, content: meta.sizeFull },
        { label: 'Components', content: components, help: MODEL_META.components },
        { label: 'Pipeline', content: pipeline, help: MODEL_META.pipeline },
        { label: 'Vectors', content: meta.vectors, help: MODEL_META.vecs },
        { label: 'Sources', content: sources, help: MODEL_META.sources },
        { label: 'Author', content: author },
        { label: 'License', content: license },
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
                <CodeBlock lang="cli" prompt="$">
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
            {meta.notes && markdownToReact(meta.notes, MARKDOWN_COMPONENTS)}
            {hasInteractiveCode && (
                <CodeBlock title="Try out the model" lang="python" executable={true}>
                    {[
                        `import spacy`,
                        `from spacy.lang.${langId}.examples import sentences `,
                        ``,
                        `nlp = spacy.load("${name}")`,
                        `doc = nlp(sentences[0])`,
                        `print(doc.text)`,
                        `for token in doc:`,
                        `    print(token.text, token.pos_, token.dep_)`,
                    ].join('\n')}
                </CodeBlock>
            )}
            {meta.accuracy && (
                <Accordion id={`${name}-accuracy`} title="Accuracy Evaluation">
                    <Table>
                        <tbody>
                            {meta.accuracy.map(({ label, value, help }) => (
                                <Tr key={`${name}-${label}`}>
                                    <Td nowrap>
                                        <InlineCode>{label.toUpperCase()}</InlineCode>
                                    </Td>
                                    <Td>{help}</Td>
                                    <Td num style={{ textAlign: 'right' }}>
                                        {value}
                                    </Td>
                                </Tr>
                            ))}
                        </tbody>
                    </Table>
                </Accordion>
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
                                    <Tr key={`${name}-${pipe}`} evenodd={false} key={pipe}>
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
            <Title title={title} teaser={`Available trained pipelines for ${title}`} />
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
                            hasExamples={meta.hasExamples}
                            prereleases={site.siteMetadata.nightly}
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
                nightly
                licenses {
                    id
                    url
                }
            }
        }
    }
`

import React, { Fragment } from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import highlightCode from 'gatsby-remark-prismjs/highlight-code.js'
import 'prismjs-bibtex'
import rangeParser from 'parse-numeric-range'
import { StaticQuery, graphql } from 'gatsby'
import { window } from 'browser-monads'

import CUSTOM_TYPES from '../../meta/type-annotations.json'
import { isString, htmlToReact } from './util'
import Link, { OptionalLink } from './link'
import GitHubCode from './github'
import classes from '../styles/code.module.sass'

const WRAP_THRESHOLD = 30
const CLI_GROUPS = ['init', 'debug', 'project', 'ray', 'huggingface-hub']

export default props => (
    <Pre>
        <Code {...props} />
    </Pre>
)

export const Pre = props => {
    return <pre className={classes.pre}>{props.children}</pre>
}

export const InlineCode = ({ wrap = false, className, children, ...props }) => {
    const codeClassNames = classNames(classes.inlineCode, className, {
        [classes.wrap]: wrap || (isString(children) && children.length >= WRAP_THRESHOLD),
    })
    return (
        <code className={codeClassNames} {...props}>
            {children}
        </code>
    )
}

InlineCode.propTypes = {
    wrap: PropTypes.bool,
    className: PropTypes.string,
    children: PropTypes.node,
}

function linkType(el, showLink = true) {
    if (!isString(el) || !el.length) return el
    const elStr = el.trim()
    if (!elStr) return el
    const typeUrl = CUSTOM_TYPES[elStr]
    const url = typeUrl == true ? DEFAULT_TYPE_URL : typeUrl
    const ws = el[0] == ' '
    return url && showLink ? (
        <Fragment>
            {ws && ' '}
            <Link to={url} hideIcon>
                {elStr}
            </Link>
        </Fragment>
    ) : (
        el
    )
}

export const TypeAnnotation = ({ lang = 'python', link = true, children }) => {
    // Hacky, but we're temporarily replacing a dot to prevent it from being split during highlighting
    const TMP_DOT = '۔'
    const code = Array.isArray(children) ? children.join('') : children || ''
    const [rawText, meta] = code.split(/(?= \(.+\)$)/)
    const rawStr = rawText.replace(/\./g, TMP_DOT)
    const rawHtml = lang === 'none' || !code ? code : highlightCode(lang, rawStr)
    const html = rawHtml.replace(new RegExp(TMP_DOT, 'g'), '.').replace(/\n/g, ' ')
    const result = htmlToReact(html)
    const elements = Array.isArray(result) ? result : [result]
    const annotClassNames = classNames(
        'type-annotation',
        `language-${lang}`,
        classes.inlineCode,
        classes.typeAnnotation,
        {
            [classes.wrap]: code.length >= WRAP_THRESHOLD,
        }
    )
    return (
        <code className={annotClassNames} aria-label="Type annotation">
            {elements.map((el, i) => (
                <Fragment key={i}>{linkType(el, !!link)}</Fragment>
            ))}
            {meta && <span className={classes.typeAnnotationMeta}>{meta}</span>}
        </code>
    )
}

function replacePrompt(line, prompt, isFirst = false) {
    let result = line
    const hasPrompt = result.startsWith(`${prompt} `)
    const showPrompt = hasPrompt || isFirst
    if (hasPrompt) result = result.slice(2)
    return result && showPrompt ? `<span data-prompt="${prompt}">${result}</span>` : result
}

function parseArgs(raw) {
    let args = raw.split(' ').filter(arg => arg)
    const result = {}
    while (args.length) {
        let opt = args.shift()
        if (opt.length > 1 && opt.startsWith('-')) {
            const isFlag = !args.length || (args[0].length > 1 && args[0].startsWith('-'))
            result[opt] = isFlag ? true : args.shift()
        } else {
            let key = opt
            if (CLI_GROUPS.includes(opt)) {
                if (args.length && !args[0].startsWith('-')) {
                    key = `${opt} ${args.shift()}`
                }
            }
            result[key] = null
        }
    }
    return result
}

function convertLine(line, i) {
    const cliRegex = /^(\$ )?python -m spacy/
    if (cliRegex.test(line)) {
        const text = line.replace(cliRegex, '')
        const args = parseArgs(text)
        const cmd = Object.keys(args).map((key, i) => {
            const value = args[key]
            return value === null || value === true || i === 0 ? key : `${key} ${value}`
        })
        return (
            <Fragment key={line}>
                <span data-prompt={i === 0 ? '$' : null} className={classes.cliArgSubtle}>
                    python -m
                </span>{' '}
                <span>spacy</span>{' '}
                {cmd.map((item, j) => {
                    const isCmd = j === 0
                    const url = isCmd ? `/api/cli#${item.replace(' ', '-')}` : null
                    const isAbstract = isString(item) && /^\[(.+)\]$/.test(item)
                    const itemClassNames = classNames(classes.cliArg, {
                        [classes.cliArgHighlight]: isCmd,
                        [classes.cliArgEmphasis]: isAbstract,
                    })
                    const text = isAbstract ? item.slice(1, -1) : item
                    return (
                        <Fragment key={j}>
                            {j !== 0 && ' '}
                            <span className={itemClassNames}>
                                <OptionalLink hidden hideIcon to={url}>
                                    {text}
                                </OptionalLink>
                            </span>
                        </Fragment>
                    )
                })}
            </Fragment>
        )
    }
    const htmlLine = replacePrompt(highlightCode('bash', line), '$')
    return htmlToReact(htmlLine)
}

function formatCode(html, lang, prompt) {
    if (lang === 'cli') {
        const lines = html
            .trim()
            .split('\n')
            .map(line =>
                line
                    .split(' | ')
                    .map((l, i) => convertLine(l, i))
                    .map((l, j) => (
                        <Fragment>
                            {j !== 0 && <span> | </span>}
                            {l}
                        </Fragment>
                    ))
            )
        return lines.map((line, i) => (
            <Fragment key={i}>
                {i !== 0 && <br />}
                {line}
            </Fragment>
        ))
    }
    const result = html
        .split('\n')
        .map((line, i) => {
            let newLine = prompt ? replacePrompt(line, prompt, i === 0) : line
            if (lang === 'diff' && !line.startsWith('<')) {
                newLine = highlightCode('python', line)
            }
            return newLine
        })
        .join('\n')
    return htmlToReact(result)
}

export class Code extends React.Component {
    state = { Juniper: null }

    static defaultProps = {
        lang: 'none',
        executable: null,
        github: false,
    }

    static propTypes = {
        lang: PropTypes.string,
        title: PropTypes.string,
        executable: PropTypes.oneOf(['true', 'false', true, false, null]),
        github: PropTypes.oneOf(['true', 'false', true, false, null]),
        prompt: PropTypes.string,
        highlight: PropTypes.string,
        className: PropTypes.string,
        children: PropTypes.node,
    }

    updateJuniper() {
        if (this.state.Juniper == null && window.Juniper !== null) {
            this.setState({ Juniper: window.Juniper })
        }
    }

    componentDidMount() {
        this.updateJuniper()
    }

    componentDidUpdate() {
        this.updateJuniper()
    }

    render() {
        const {
            lang,
            title,
            executable,
            github,
            prompt,
            wrap,
            highlight,
            className,
            children,
        } = this.props
        const codeClassNames = classNames(classes.code, className, `language-${lang}`, {
            [classes.wrap]: !!highlight || !!wrap || lang === 'cli',
            [classes.cli]: lang === 'cli',
        })
        const ghClassNames = classNames(codeClassNames, classes.maxHeight)
        const { Juniper } = this.state

        if (github) {
            return <GitHubCode url={children} className={ghClassNames} lang={lang} />
        }
        if (!!executable && Juniper) {
            return (
                <JuniperWrapper Juniper={Juniper} title={title} lang={lang}>
                    {children}
                </JuniperWrapper>
            )
        }

        const codeText = Array.isArray(children) ? children.join('') : children || ''
        const highlightRange = highlight ? rangeParser.parse(highlight).filter(n => n > 0) : []
        const rawHtml = ['none', 'cli'].includes(lang)
            ? codeText
            : highlightCode(lang, codeText, highlightRange)
        const html = formatCode(rawHtml, lang, prompt)
        return (
            <>
                {title && <h4 className={classes.title}>{title}</h4>}
                <code className={codeClassNames}>{html}</code>
            </>
        )
    }
}

const JuniperWrapper = ({ Juniper, title, lang, children }) => (
    <StaticQuery
        query={query}
        render={data => {
            const { binderUrl, binderBranch, binderVersion } = data.site.siteMetadata
            const juniperTitle = title || 'Editable Code'
            return (
                <div className={classes.juniperWrapper}>
                    <h4 className={classes.juniperTitle}>
                        {juniperTitle}
                        <span className={classes.juniperMeta}>
                            spaCy v{binderVersion} &middot; Python 3 &middot; via{' '}
                            <Link to="https://mybinder.org/" hidden>
                                Binder
                            </Link>
                        </span>
                    </h4>

                    <Juniper
                        repo={binderUrl}
                        branch={binderBranch}
                        lang={lang}
                        classNames={{
                            cell: classes.juniperCell,
                            input: classes.juniperInput,
                            button: classes.juniperButton,
                            output: classes.juniperOutput,
                        }}
                    >
                        {children}
                    </Juniper>
                </div>
            )
        }}
    />
)

const query = graphql`
    query JuniperQuery {
        site {
            siteMetadata {
                binderUrl
                binderBranch
                binderVersion
            }
        }
    }
`

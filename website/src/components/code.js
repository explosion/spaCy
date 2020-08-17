import React, { Fragment } from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import highlightCode from 'gatsby-remark-prismjs/highlight-code.js'
import rangeParser from 'parse-numeric-range'
import { StaticQuery, graphql } from 'gatsby'
import { window } from 'browser-monads'

import CUSTOM_TYPES from '../../meta/type-annotations.json'
import { isString, htmlToReact } from './util'
import Link from './link'
import GitHubCode from './github'
import classes from '../styles/code.module.sass'

const WRAP_THRESHOLD = 30

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
            [classes.wrap]: !!highlight || !!wrap,
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
        const html = lang === 'none' ? codeText : highlightCode(lang, codeText, highlightRange)

        return (
            <>
                {title && <h4 className={classes.title}>{title}</h4>}
                <code className={codeClassNames} data-prompt={prompt}>
                    {htmlToReact(html)}
                </code>
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

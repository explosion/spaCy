import React, { Fragment } from 'react'
import classNames from 'classnames'
import Prism from 'prismjs'
import CUSTOM_TYPES from '../../meta/type-annotations.json'
import { isString, htmlToReact } from './util'
import Link from './link'
import classes from '../styles/code.module.sass'

export const WRAP_THRESHOLD = 30

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
    const rawHtml =
        lang === 'none' || !code ? code : Prism.highlight(rawStr, Prism.languages[lang], lang)
    const html = rawHtml.replace(new RegExp(TMP_DOT, 'g'), '.').replace(/\n/g, ' ')
    const result = htmlToReact(html)
    const elements = Array.isArray(result) ? result : [result]
    const annotClassNames = classNames(
        'type-annotation',
        `language-${lang}`,
        classes['inline-code'],
        classes['type-annotation'],
        {
            [classes['wrap']]: code.length >= WRAP_THRESHOLD,
        }
    )
    return (
        <span className={annotClassNames} role="code" aria-label="Type annotation">
            {elements.map((el, i) => (
                <Fragment key={i}>{linkType(el, !!link)}</Fragment>
            ))}
            {meta && <span className={classes['type-annotation-meta']}>{meta}</span>}
        </span>
    )
}

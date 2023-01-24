import React from 'react'
import classNames from 'classnames'
import CUSTOM_TYPES from '../../meta/type-annotations.json'
import Link from './link'
import classes from '../styles/code.module.sass'

export const WRAP_THRESHOLD = 30

const specialCharacterList = ['[', ']', ',', ', ']

const highlight = (element) =>
    specialCharacterList.includes(element) ? (
        <span className={classes['cli-arg-subtle']}>{element}</span>
    ) : (
        element
    )

function linkType(el, showLink = true, key) {
    if (!el.length) return el
    const elStr = el.trim()
    if (!elStr) return el
    const typeUrl = CUSTOM_TYPES[elStr]
    const url = typeUrl == true ? DEFAULT_TYPE_URL : typeUrl
    return url && showLink ? (
        <Link to={url} hideIcon key={key}>
            {elStr}
        </Link>
    ) : (
        highlight(el)
    )
}

export const TypeAnnotation = ({ lang = 'python', link = true, children }) => {
    const code = Array.isArray(children) ? children.join('') : children || ''
    const [rawText, meta] = code.split(/(?= \(.+\)$)/)
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
            {rawText.split(/(\[|\]|,)/).map((el, i) => linkType(el, !!link, i))}
            {meta && <span className={classes['type-annotation-meta']}>{meta}</span>}
        </span>
    )
}

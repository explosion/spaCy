import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import { isString } from './util'
import classes from '../styles/code.module.sass'

const WRAP_THRESHOLD = 30

export const InlineCode = ({ wrap = false, className, children, ...props }) => {
    const codeClassNames = classNames(classes['inline-code'], className, {
        [classes['wrap']]: wrap || (isString(children) && children.length >= WRAP_THRESHOLD),
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

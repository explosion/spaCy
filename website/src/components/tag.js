import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'

import { isString } from './util'
import Icon from './icon'
import classes from '../styles/tag.module.sass'

const Tag = ({ spaced, variant, tooltip, children }) => {
    if (variant === 'new') {
        const isValid = isString(children) && !isNaN(children)
        const version = isValid ? Number(children).toFixed(1) : children
        const tooltipText = `This feature is new and was introduced in spaCy v${version}`
        return (
            <TagTemplate spaced={spaced} tooltip={tooltipText}>
                v{version}
            </TagTemplate>
        )
    }
    if (variant === 'model') {
        const tooltipText = `To use this functionality, spaCy needs a model to be installed that supports the following capabilities: ${children}`
        return (
            <TagTemplate spaced={spaced} tooltip={tooltipText}>
                Needs model
            </TagTemplate>
        )
    }
    return (
        <TagTemplate spaced={spaced} tooltip={tooltip}>
            {children}
        </TagTemplate>
    )
}

const TagTemplate = ({ spaced, tooltip, children }) => {
    const tagClassNames = classNames(classes.root, {
        [classes.spaced]: spaced,
    })
    return (
        <span className={tagClassNames} data-tooltip={tooltip}>
            {children}
            {tooltip && <Icon name="help" width={12} className={classes.icon} />}
        </span>
    )
}

Tag.defaultProps = {
    spaced: false,
}

Tag.propTypes = {
    spaced: PropTypes.bool,
    tooltip: PropTypes.string,
    children: PropTypes.node.isRequired,
}

export default Tag

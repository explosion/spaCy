import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'

import Icon from './icon'
import classes from '../styles/infobox.module.sass'

export default function Infobox({ title, emoji, id, variant = 'default', className, children }) {
    const infoboxClassNames = classNames(classes.root, className, {
        [classes.warning]: variant === 'warning',
        [classes.danger]: variant === 'danger',
    })
    return (
        <aside className={infoboxClassNames} id={id}>
            {title && (
                <h4 className={classes.title}>
                    {variant !== 'default' && (
                        <Icon width={18} name={variant} inline className={classes.icon} />
                    )}
                    <span className={classes.titleText}>
                        {emoji && (
                            <span className={classes.emoji} aria-hidden="true">
                                {emoji}
                            </span>
                        )}
                        {title}
                    </span>
                </h4>
            )}
            {children}
        </aside>
    )
}

Infobox.propTypes = {
    title: PropTypes.node,
    id: PropTypes.string,
    variant: PropTypes.oneOf(['default', 'warning', 'danger']),
    className: PropTypes.string,
    children: PropTypes.node.isRequired,
}

import React, { Fragment } from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'

import Icon from './icon'
import classes from '../styles/infobox.module.sass'

export default function Infobox({
    title,
    emoji,
    id,
    variant = 'default',
    list = false,
    className,
    children,
}) {
    const Wrapper = id ? 'div' : Fragment
    const infoboxClassNames = classNames(classes.root, className, {
        [classes.list]: !!list,
        [classes.warning]: variant === 'warning',
        [classes.danger]: variant === 'danger',
    })
    return (
        <Wrapper>
            {id && <a id={id} />}
            <aside className={infoboxClassNames}>
                {title && (
                    <h4 className={classes.title}>
                        {variant !== 'default' && !emoji && (
                            <Icon width={18} name={variant} inline className={classes.icon} />
                        )}
                        <span>
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
        </Wrapper>
    )
}

Infobox.propTypes = {
    title: PropTypes.node,
    id: PropTypes.string,
    variant: PropTypes.oneOf(['default', 'warning', 'danger']),
    className: PropTypes.string,
    children: PropTypes.node.isRequired,
}

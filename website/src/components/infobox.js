import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'

import Icon from './icon'
import classes from '../styles/infobox.module.sass'

const Infobox = ({ title, id, variant, className, children }) => {
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
                    <span className={classes.titleText}>{title}</span>
                </h4>
            )}
            {children}
        </aside>
    )
}

Infobox.defaultProps = {
    variant: 'default',
}

Infobox.propTypes = {
    title: PropTypes.string,
    id: PropTypes.string,
    variant: PropTypes.oneOf(['default', 'warning', 'danger']),
    className: PropTypes.string,
    children: PropTypes.node.isRequired,
}

export default Infobox

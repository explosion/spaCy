import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'

import Link from './link'
import Icon from './icon'
import classes from '../styles/button.module.sass'

export default function Button({
    to,
    variant = 'secondary',
    large = false,
    icon,
    className,
    children,
    ...props
}) {
    const buttonClassNames = classNames(classes.root, className, {
        [classes.large]: large,
        [classes.primary]: variant === 'primary',
        [classes.secondary]: variant === 'secondary',
        [classes.tertiary]: variant === 'tertiary',
    })
    return (
        <Link to={to} className={buttonClassNames} hideIcon={true} {...props}>
            {icon && <Icon name={icon} width={large ? 16 : 14} inline />}
            {children}
        </Link>
    )
}

Button.propTypes = {
    to: PropTypes.string,
    variant: PropTypes.oneOf(['primary', 'secondary', 'tertiary']),
    large: PropTypes.bool,
    icon: PropTypes.string,
    className: PropTypes.string,
}

import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'

import Link from './link'
import Icon from './icon'
import classes from '../styles/button.module.sass'

const Button = ({ to, variant, large, icon, className, children, ...props }) => {
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

Button.defaultProps = {
    variant: 'secondary',
    large: false,
}

Button.propTypes = {
    to: PropTypes.string.isRequired,
    variant: PropTypes.oneOf(['primary', 'secondary', 'tertiary']),
    large: PropTypes.bool,
    icon: PropTypes.string,
    className: PropTypes.string,
}

export default Button

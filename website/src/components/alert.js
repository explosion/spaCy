import React, { useState } from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'

import Icon from './icon'
import classes from '../styles/alert.module.sass'

export default function Alert({ title, icon, variant, closeOnClick = true, children }) {
    const [visible, setVisible] = useState(true)
    const alertClassNames = classNames(classes.root, {
        [classes.warning]: variant === 'warning',
        [classes.clickable]: !!closeOnClick,
    })
    const handleClick = () => !!closeOnClick && setVisible(false)
    return !visible ? null : (
        <aside className={alertClassNames} role="alert" onClick={handleClick}>
            {icon && <Icon name={icon} width={18} inline />}
            {title && <strong>{title}</strong>} {children}
        </aside>
    )
}

Alert.propTypes = {
    title: PropTypes.string,
    icon: PropTypes.string,
    variant: PropTypes.oneOf(['warning']),
    closeOnClick: PropTypes.bool,
    children: PropTypes.node,
}

import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'

import Link from './link'
import Icon from './icon'
import { github } from './util'
import { ReactComponent as Logo } from '../images/logo.svg'
import classes from '../styles/navigation.module.sass'

const Navigation = ({ title, items, section, children }) => (
    <nav className={classes.root}>
        <Link to="/" aria-label={title} hidden>
            <h1 className={classes.title}>{title}</h1>
            <Logo className={classes.logo} width={300} height={96} />
        </Link>

        <ul className={classes.menu}>
            {items.map(({ text, url }, i) => {
                const isActive = section && text.toLowerCase() === section
                const itemClassNames = classNames(classes.item, {
                    [classes.isActive]: isActive,
                })
                return (
                    <li key={i} className={itemClassNames}>
                        <Link to={url} tabIndex={isActive ? '-1' : null} hidden>
                            {text}
                        </Link>
                    </li>
                )
            })}
            <li className={classes.item}>
                <Link to={github()} aria-label="GitHub" hidden>
                    <Icon name="github" />
                </Link>
            </li>
        </ul>
        {children}
    </nav>
)

Navigation.defaultProps = {
    items: [],
}

Navigation.propTypes = {
    title: PropTypes.string.isRequired,
    items: PropTypes.arrayOf(
        PropTypes.shape({
            text: PropTypes.string.isRequired,
            url: PropTypes.string.isRequired,
        })
    ),
    section: PropTypes.string,
}

export default Navigation

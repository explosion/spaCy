import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'

import Link from './link'
import Icon from './icon'
import Dropdown from './dropdown'
import { github } from './util'
import { ReactComponent as Logo } from '../images/logo.svg'
import classes from '../styles/navigation.module.sass'

const NavigationDropdown = ({ items = [], section }) => {
    const active = items.find(({ text }) => text.toLowerCase() === section)
    const defaultValue = active ? active.url : 'title'
    return (
        <Dropdown defaultValue={defaultValue} className={classes.dropdown}>
            <option value="title" disabled>
                Menu
            </option>
            {items.map(({ text, url }, i) => (
                <option key={i} value={url}>
                    {text}
                </option>
            ))}
        </Dropdown>
    )
}

export default function Navigation({ title, items = [], section, search, children }) {
    return (
        <nav className={classes.root}>
            <Link to="/" aria-label={title} hidden>
                <h1 className={classes.title}>{title}</h1>
                <Logo className={classes.logo} width={300} height={96} />
            </Link>

            <div className={classes.menu}>
                <NavigationDropdown items={items} section={section} />

                <ul className={classes.list}>
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
                {search && <div className={classes.search}>{search}</div>}
            </div>
            {children}
        </nav>
    )
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
    search: PropTypes.node,
}

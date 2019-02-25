import React, { useState, useEffect, useRef } from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import { window } from 'browser-monads'

import Link from './link'
import classes from '../styles/sidebar.module.sass'

const Sidebar = ({ items, pageMenu, slug }) => {
    const [initialized, setInitialized] = useState(false)
    const [activeSection, setActiveSection] = useState(null)
    const activeRef = useRef()
    const handleInView = ({ detail }) => setActiveSection(detail)

    useEffect(() => {
        window.addEventListener('inview', handleInView, { passive: true })
        if (!initialized) {
            if (activeRef && activeRef.current) {
                activeRef.current.scrollIntoView({ block: 'center' })
            }
            setInitialized(true)
        }
        return () => {
            window.removeEventListener('inview', handleInView)
        }
    }, [])

    return (
        <menu className={classNames('sidebar', classes.root)}>
            {items.map((section, i) => (
                <ul className={classes.section} key={i}>
                    <li className={classNames('h0', classes.label)}>{section.label}</li>
                    {section.items.map(({ text, url, onClick, menu, isActive }, j) => {
                        const currentMenu = menu || pageMenu || []
                        const active = isActive || slug === url
                        const itemClassNames = classNames(classes.link, {
                            [classes.isActive]: active,
                        })

                        return (
                            <li key={j} ref={active ? activeRef : null}>
                                <Link
                                    to={url}
                                    onClick={onClick}
                                    className={itemClassNames}
                                    activeClassName={classNames('is-active', classes.isActive)}
                                    hideIcon
                                >
                                    {text}
                                </Link>
                                {active && !!currentMenu.length && (
                                    <ul className={classes.crumbs}>
                                        {currentMenu.map(crumb => {
                                            const currentActive = activeSection || currentMenu[0].id
                                            const crumbClassNames = classNames(classes.crumb, {
                                                [classes.crumbActive]: currentActive === crumb.id,
                                            })
                                            return (
                                                <li className={crumbClassNames} key={crumb.id}>
                                                    <a href={`#${crumb.id}`}>{crumb.text}</a>
                                                </li>
                                            )
                                        })}
                                    </ul>
                                )}
                            </li>
                        )
                    })}
                </ul>
            ))}
        </menu>
    )
}

Sidebar.defaultProps = {
    items: [],
    pageMenu: [],
}

Sidebar.propTypes = {
    items: PropTypes.arrayOf(
        PropTypes.shape({
            label: PropTypes.string.isRequired,
            items: PropTypes.arrayOf(
                PropTypes.shape({
                    text: PropTypes.string.isRequired,
                    url: PropTypes.string,
                    onClick: PropTypes.func,
                    menu: PropTypes.arrayOf(
                        PropTypes.shape({
                            text: PropTypes.string.isRequired,
                            id: PropTypes.string.isRequired,
                        })
                    ),
                })
            ).isRequired,
        })
    ),
    pageMenu: PropTypes.arrayOf(
        PropTypes.shape({
            text: PropTypes.string.isRequired,
            id: PropTypes.string.isRequired,
        })
    ),
}

export default Sidebar

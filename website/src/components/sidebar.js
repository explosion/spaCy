import React, { useState, useEffect, useRef } from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import { window } from 'browser-monads'

import Link from './link'
import Tag from './tag'
import Dropdown from './dropdown'
import classes from '../styles/sidebar.module.sass'

function getActiveHeading(items, slug) {
    if (/^\/?universe/.test(slug)) return 'Universe'
    for (let section of items) {
        for (let { isActive, url } of section.items) {
            if (isActive || slug === url) {
                return section.label
            }
        }
    }
    return 'Documentation'
}

const DropdownNavigation = ({ items, defaultValue }) => {
    return (
        <div className={classes.dropdown}>
            <Dropdown className={classes.dropdownSelect} defaultValue={defaultValue}>
                <option disabled>Select page...</option>
                {items.map((section, i) =>
                    section.items.map(({ text, url }, j) => (
                        <option value={url} key={j}>
                            {section.label} &rsaquo; {text}
                        </option>
                    ))
                )}
            </Dropdown>
        </div>
    )
}

export default function Sidebar({ items = [], pageMenu = [], slug }) {
    const [initialized, setInitialized] = useState(false)
    const [activeSection, setActiveSection] = useState(null)
    const activeRef = useRef()
    const activeHeading = getActiveHeading(items, slug)

    useEffect(() => {
        const handleInView = ({ detail }) => setActiveSection(detail)
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
    }, [initialized])

    return (
        <menu className={classNames('sidebar', classes.root)}>
            <h1 hidden aria-hidden="true" className={classNames('h0', classes.activeHeading)}>
                {activeHeading}
            </h1>
            <DropdownNavigation items={items} defaultValue={slug} />
            {items.map((section, i) => (
                <ul className={classes.section} key={i}>
                    <li className={classes.label}>{section.label}</li>
                    {section.items.map(({ text, url, tag, onClick, menu, isActive }, j) => {
                        const currentMenu = menu || pageMenu || []
                        const active = isActive || slug === url
                        const itemClassNames = classNames(classes.link, {
                            [classes.isActive]: active,
                            'is-active': active,
                        })

                        return (
                            <li key={j} ref={active ? activeRef : null}>
                                <Link
                                    to={url}
                                    onClick={onClick}
                                    className={itemClassNames}
                                    hideIcon
                                >
                                    {text}
                                    {tag && <Tag spaced>{tag}</Tag>}
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

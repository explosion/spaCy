import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'

import patternBlue from '../images/pattern_blue.jpg'
import patternGreen from '../images/pattern_green.jpg'
import patternPurple from '../images/pattern_purple.jpg'
import patternNightly from '../images/pattern_nightly.jpg'
import patternLegacy from '../images/pattern_legacy.jpg'
import classes from '../styles/main.module.sass'

const patterns = {
    blue: patternBlue,
    green: patternGreen,
    purple: patternPurple,
    nightly: patternNightly,
    legacy: patternLegacy,
}

export const Content = ({ Component = 'div', className, children }) => (
    <Component className={classNames(classes.content, className)}>{children}</Component>
)

export default function Main({
    sidebar = false,
    asides = false,
    wrapContent = false,
    theme = 'blue',
    footer,
    children,
}) {
    const pattern = patterns[theme]
    const mainClassNames = classNames(classes.root, {
        [classes.withSidebar]: sidebar,
        [classes.withAsides]: asides,
    })

    return (
        <main className={mainClassNames}>
            {wrapContent ? <Content Component="article">{children}</Content> : children}
            {asides && (
                <div className={classes.asides} style={{ backgroundImage: `url(${pattern}` }} />
            )}
            {footer}
        </main>
    )
}

Main.propTypes = {
    sidebar: PropTypes.bool,
    asides: PropTypes.bool,
    wrapContent: PropTypes.bool,
    theme: PropTypes.string.isRequired,
    footer: PropTypes.node,
}

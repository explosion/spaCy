import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'

import patternBlue from '../images/pattern_blue.jpg'
import patternGreen from '../images/pattern_green.jpg'
import patternPurple from '../images/pattern_purple.jpg'
import classes from '../styles/main.module.sass'

const patterns = { blue: patternBlue, green: patternGreen, purple: patternPurple }

export const Content = ({ Component = 'div', className, children }) => (
    <Component className={classNames(classes.content, className)}>{children}</Component>
)

const Main = ({ sidebar, asides, wrapContent, theme, footer, children }) => {
    const mainClassNames = classNames(classes.root, {
        [classes.withSidebar]: sidebar,
        [classes.withAsides]: asides,
    })

    return (
        <main className={mainClassNames}>
            {wrapContent ? <Content Component="article">{children}</Content> : children}
            {asides && (
                <div
                    className={classes.asides}
                    style={{ backgroundImage: `url(${patterns[theme]}` }}
                />
            )}
            {footer}
        </main>
    )
}

Main.defaultProps = {
    sidebar: false,
    asides: false,
    wrapContent: false,
    theme: 'blue',
}

Main.propTypes = {
    sidebar: PropTypes.bool,
    asides: PropTypes.bool,
    wrapContent: PropTypes.bool,
    theme: PropTypes.string.isRequired,
    footer: PropTypes.node,
}

export default Main

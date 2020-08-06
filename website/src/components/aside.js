import React from 'react'
import PropTypes from 'prop-types'

import classes from '../styles/aside.module.sass'

export default function Aside({ title, children }) {
    return (
        <aside className={classes.root}>
            <div className={classes.content} role="complementary">
                <div className={classes.text}>
                    {title && <h4 className={classes.title}>{title}</h4>}
                    {children}
                </div>
            </div>
        </aside>
    )
}

Aside.propTypes = {
    title: PropTypes.string,
    children: PropTypes.node.isRequired,
}

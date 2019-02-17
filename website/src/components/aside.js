import React from 'react'
import PropTypes from 'prop-types'

import classes from '../styles/aside.module.sass'

const Aside = ({ title, children }) => (
    <aside className={classes.root}>
        <div className={classes.content} role="complementary">
            <div className={classes.text}>
                {title && <h4 className={classes.title}>{title}</h4>}
                {children}
            </div>
        </div>
    </aside>
)

Aside.propTypes = {
    title: PropTypes.string,
    children: PropTypes.node.isRequired,
}

export default Aside

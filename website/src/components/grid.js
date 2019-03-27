import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'

import classes from '../styles/grid.module.sass'

const Grid = ({ cols, narrow, gutterBottom, className, children }) => {
    const gridClassNames = classNames(classes.root, className, {
        [classes.narrow]: narrow,
        [classes.spacing]: gutterBottom,
        [classes.half]: cols === 2,
        [classes.third]: cols === 3,
        [classes.quarter]: cols === 4,
    })
    return <div className={gridClassNames}>{children}</div>
}

Grid.defaultProps = {
    cols: 1,
    narrow: false,
    gutterBottom: true,
}

Grid.propTypes = {
    cols: PropTypes.oneOf([1, 2, 3, 4]),
    narrow: PropTypes.bool,
    gutterBottom: PropTypes.bool,
}

export default Grid

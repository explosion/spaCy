import React from 'react'
import PropTypes from 'prop-types'

import Icon from './icon'
import Link from './link'
import { Label } from './typography'

import classes from '../styles/readnext.module.sass'

export default function ReadNext({ title, to }) {
    return (
        <div className={classes.root}>
            <Link to={to} hidden>
                <Label>Read next</Label>
                {title}
            </Link>
            <Link to={to} hidden className={classes.icon} aria-hidden="true">
                <Icon name="arrowright" />
            </Link>
        </div>
    )
}

ReadNext.propTypes = {
    title: PropTypes.string.isRequired,
    to: PropTypes.string.isRequired,
}

import React from 'react'
import PropTypes from 'prop-types'

import Icon from './icon'
import Link from './link'
import { Label } from './typography'

import classes from '../styles/readnext.module.sass'

export default function ReadNext({ title, to }) {
    return (
        <div className={classes.root}>
            <Link to={to} noLinkLayout>
                <Label>Read next</Label>
                {title}
            </Link>
            <Link to={to} noLinkLayout className={classes.icon}>
                <Icon name="arrowright" aria-hidden="true" />
            </Link>
        </div>
    )
}

ReadNext.propTypes = {
    title: PropTypes.string.isRequired,
    to: PropTypes.string.isRequired,
}

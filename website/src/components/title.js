import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'

import Button from './button'
import Tag from './tag'
import { H1 } from './typography'

import classes from '../styles/title.module.sass'

const Title = ({ id, title, tag, version, teaser, source, image, children, ...props }) => (
    <header className={classes.root}>
        {(image || source) && (
            <div className={classes.corner}>
                {source && (
                    <Button to={source} icon="code">
                        Source
                    </Button>
                )}

                {image && (
                    <div className={classes.image}>
                        <img src={image} width={100} height={100} alt="" />
                    </div>
                )}
            </div>
        )}
        <H1 className={classes.h1} id={id} {...props}>
            {title}
        </H1>
        {tag && <Tag spaced>{tag}</Tag>}
        {version && (
            <Tag variant="new" spaced>
                {version}
            </Tag>
        )}

        {teaser && <div className={classNames('heading-teaser', classes.teaser)}>{teaser}</div>}

        {children}
    </header>
)

Title.propTypes = {
    title: PropTypes.string,
    tag: PropTypes.string,
    teaser: PropTypes.node,
    source: PropTypes.string,
    image: PropTypes.string,
    children: PropTypes.node,
}

export default Title

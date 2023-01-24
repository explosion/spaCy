import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import ImageNext from 'next/image'

import Link from './link'
import { H5 } from './typography'
import classes from '../styles/card.module.sass'

export default function Card({ title, to, image, header, small, onClick, children }) {
    return (
        <div className={classNames(classes.root, { [classes.small]: !!small })}>
            {header && (
                <Link to={to} onClick={onClick} noLinkLayout>
                    {header}
                </Link>
            )}
            {(title || image) && (
                <H5 className={classes.title}>
                    {image && (
                        <div className={classes.image}>
                            <ImageNext src={image} height={35} width={35} alt={`${title} Logo`} />
                        </div>
                    )}
                    {title && (
                        <Link to={to} onClick={onClick} noLinkLayout>
                            {title}
                        </Link>
                    )}
                </H5>
            )}
            <Link to={to} onClick={onClick} noLinkLayout>
                {children}
            </Link>
        </div>
    )
}

Card.propTypes = {
    title: PropTypes.node,
    header: PropTypes.node,
    to: PropTypes.string,
    image: PropTypes.string,
    onClick: PropTypes.func,
    children: PropTypes.node,
}

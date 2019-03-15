import React from 'react'
import PropTypes from 'prop-types'

import Link from './link'
import { H5 } from './typography'
import classes from '../styles/card.module.sass'

const Card = ({ title, to, image, header, onClick, children }) => (
    <div className={classes.root}>
        {header && (
            <Link to={to} onClick={onClick} hidden>
                {header}
            </Link>
        )}
        <H5>
            {image && (
                <div className={classes.image}>
                    <img src={image} width={35} alt="" />
                </div>
            )}
            {title && (
                <Link to={to} onClick={onClick} hidden>
                    {title}
                </Link>
            )}
        </H5>
        <Link to={to} onClick={onClick} hidden>
            {children}
        </Link>
    </div>
)

Card.propTypes = {
    title: PropTypes.string,
    to: PropTypes.string,
    image: PropTypes.string,
    card: PropTypes.node,
    onClick: PropTypes.func,
    children: PropTypes.node,
}

export default Card

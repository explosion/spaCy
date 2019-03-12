import React, { useState } from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'

import Link from './link'
import classes from '../styles/accordion.module.sass'

const Accordion = ({ title, id, expanded, children }) => {
    const [isExpanded, setIsExpanded] = useState(expanded)
    const contentClassNames = classNames(classes.content, {
        [classes.hidden]: !isExpanded,
    })
    const iconClassNames = classNames({
        [classes.hidden]: isExpanded,
    })
    return (
        <section id={id}>
            <div className={classes.root}>
                <h3>
                    <button
                        className={classes.button}
                        aria-expanded={String(isExpanded)}
                        onClick={() => setIsExpanded(!isExpanded)}
                    >
                        <span>
                            {title}
                            {isExpanded && !!id && (
                                <Link to={`#${id}`} className={classes.anchor} hidden>
                                    &para;
                                </Link>
                            )}
                        </span>
                        <svg
                            className={classes.icon}
                            width={20}
                            height={20}
                            viewBox="0 0 10 10"
                            aria-hidden="true"
                            focusable="false"
                        >
                            <rect className={iconClassNames} height={8} width={2} x={4} y={1} />
                            <rect height={2} width={8} x={1} y={4} />
                        </svg>
                    </button>
                </h3>
                <div className={contentClassNames}>{children}</div>
            </div>
        </section>
    )
}

Accordion.defaultProps = {
    expanded: false,
}

Accordion.propTypes = {
    title: PropTypes.string,
    id: PropTypes.string,
    children: PropTypes.node.isRequired,
}

export default Accordion

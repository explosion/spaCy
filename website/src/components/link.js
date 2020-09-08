import React, { Fragment } from 'react'
import PropTypes from 'prop-types'
import { Link as GatsbyLink } from 'gatsby'
import classNames from 'classnames'

import Icon from './icon'
import classes from '../styles/link.module.sass'
import { isString, isImage } from './util'

const internalRegex = /(http(s?)):\/\/(prodi.gy|spacy.io|irl.spacy.io|explosion.ai|course.spacy.io)/gi

const Whitespace = ({ children }) => (
    // Ensure that links are always wrapped in spaces
    <> {children} </>
)

function getIcon(dest) {
    if (/(github.com)/.test(dest)) return 'code'
    if (/^\/?api\/architectures#/.test(dest)) return 'network'
    if (/^\/?api/.test(dest)) return 'docs'
    if (/^\/?models\/(.+)/.test(dest)) return 'package'
    return null
}

export default function Link({
    children,
    to,
    href,
    onClick,
    activeClassName,
    hidden = false,
    hideIcon = false,
    ws = false,
    forceExternal = false,
    className,
    ...other
}) {
    const dest = to || href
    const external = forceExternal || /(http(s?)):\/\//gi.test(dest)
    const icon = getIcon(dest)
    const withIcon = !hidden && !hideIcon && !!icon && !isImage(children)
    const sourceWithText = withIcon && isString(children)
    const linkClassNames = classNames(classes.root, className, {
        [classes.hidden]: hidden,
        [classes.nowrap]: (withIcon && !sourceWithText) || icon === 'network',
        [classes.withIcon]: withIcon,
    })
    const Wrapper = ws ? Whitespace : Fragment
    const content = (
        <>
            {sourceWithText ? <span className={classes.sourceText}>{children}</span> : children}
            {withIcon && <Icon name={icon} width={16} inline className={classes.icon} />}
        </>
    )

    if (!external) {
        if ((dest && /^#/.test(dest)) || onClick) {
            return (
                <Wrapper>
                    <a href={dest} onClick={onClick} className={linkClassNames}>
                        {children}
                    </a>
                </Wrapper>
            )
        }
        return (
            <Wrapper>
                <GatsbyLink
                    to={dest}
                    className={linkClassNames}
                    activeClassName={activeClassName}
                    {...other}
                >
                    {content}
                </GatsbyLink>
            </Wrapper>
        )
    }
    const isInternal = internalRegex.test(dest)
    const rel = isInternal ? null : 'noopener nofollow noreferrer'
    return (
        <Wrapper>
            <a href={dest} className={linkClassNames} target="_blank" rel={rel} {...other}>
                {content}
            </a>
        </Wrapper>
    )
}

export const OptionalLink = ({ to, href, children, ...props }) => {
    const dest = to || href
    return dest ? (
        <Link to={dest} {...props}>
            {children}
        </Link>
    ) : (
        children || null
    )
}

Link.propTypes = {
    children: PropTypes.node.isRequired,
    to: PropTypes.string,
    href: PropTypes.string,
    onClick: PropTypes.func,
    activeClassName: PropTypes.string,
    hidden: PropTypes.bool,
    hideIcon: PropTypes.bool,
    ws: PropTypes.bool,
    className: PropTypes.string,
}

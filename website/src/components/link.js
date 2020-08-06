import React, { Fragment } from 'react'
import PropTypes from 'prop-types'
import { Link as GatsbyLink } from 'gatsby'
import { OutboundLink } from 'gatsby-plugin-google-analytics'
import classNames from 'classnames'

import Icon from './icon'
import classes from '../styles/link.module.sass'
import { isString } from './util'

const internalRegex = /(http(s?)):\/\/(prodi.gy|spacy.io|irl.spacy.io)/gi

const Whitespace = ({ children }) => (
    // Ensure that links are always wrapped in spaces
    <> {children} </>
)

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
    const isApi = !external && !hidden && !hideIcon && /^\/?api/.test(dest)
    const isArch = !external && !hidden && !hideIcon && /^\/?api\/architectures#/.test(dest)
    const isSource = external && !hidden && !hideIcon && /(github.com)/.test(dest)
    const withIcon = isApi || isArch || isSource
    const sourceWithText = withIcon && isString(children)
    const linkClassNames = classNames(classes.root, className, {
        [classes.hidden]: hidden,
        [classes.nowrap]: (withIcon && !sourceWithText) || isArch,
        [classes.withIcon]: withIcon,
    })
    const Wrapper = ws ? Whitespace : Fragment
    const icon = isArch ? 'network' : isApi ? 'docs' : isSource ? 'code' : null
    const content = (
        <>
            {sourceWithText ? <span className={classes.sourceText}>{children}</span> : children}
            {icon && <Icon name={icon} width={16} inline className={classes.icon} />}
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
            <OutboundLink
                href={dest}
                className={linkClassNames}
                target="_blank"
                rel={rel}
                {...other}
            >
                {content}
            </OutboundLink>
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

import React, { Fragment } from 'react'
import PropTypes from 'prop-types'
import { Link as GatsbyLink } from 'gatsby'
import { OutboundLink } from 'gatsby-plugin-google-analytics'
import classNames from 'classnames'

import Icon from './icon'
import classes from '../styles/link.module.sass'
import { isString } from './util'

const Whitespace = ({ children }) => (
    // Ensure that links are always wrapped in spaces
    <> {children} </>
)

const Link = ({
    children,
    to,
    href,
    onClick,
    activeClassName,
    hidden,
    hideIcon,
    ws,
    forceExternal,
    className,
    ...other
}) => {
    const dest = to || href
    const external = forceExternal || /(http(s?)):\/\//gi.test(dest)
    const isApi = !external && !hidden && !hideIcon && /^\/?api/.test(dest)
    const isSource = external && !hidden && !hideIcon && /(github.com)/.test(dest)
    const sourceWithText = (isSource || isApi) && isString(children)
    const linkClassNames = classNames(classes.root, className, {
        [classes.hidden]: hidden,
        [classes.nowrap]: (isApi || isSource) && !sourceWithText,
        [classes.withIcon]: isApi || isSource,
    })
    const Wrapper = ws ? Whitespace : Fragment
    const content = (
        <>
            {sourceWithText ? <span className={classes.sourceText}>{children}</span> : children}
            {isApi && <Icon name="docs" width={16} inline className={classes.icon} />}
            {isSource && <Icon name="code" width={16} inline className={classes.icon} />}
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
    return (
        <Wrapper>
            <OutboundLink
                href={dest}
                className={linkClassNames}
                target="_blank"
                rel="noopener nofollow noreferrer"
                {...other}
            >
                {content}
            </OutboundLink>
        </Wrapper>
    )
}

Link.defaultProps = {
    hidden: false,
    hideIcon: false,
    ws: false,
    forceExternal: false,
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

export default Link

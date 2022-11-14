import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'

import Tag from './tag'
import Button from './button'
import Icon from './icon'
import { isString, github, headingTextClassName } from './util'
import classes from '../styles/typography.module.sass'

export const H1 = ({ Component = 'h1', className, ...props }) => (
    <Headline
        Component={Component}
        className={classNames(classes.h1, className)}
        permalink={false}
        {...props}
    />
)
export const H2 = ({ className, ...props }) => (
    <Headline Component="h2" className={classNames(classes.h2, className)} {...props} />
)
export const H3 = ({ className, ...props }) => (
    <Headline Component="h3" className={classNames(classes.h3, className)} {...props} />
)
export const H4 = ({ className, ...props }) => (
    <Headline Component="h4" className={classNames(classes.h4, className)} {...props} />
)
export const H5 = ({ className, ...props }) => (
    <Headline Component="h5" className={classNames(classes.h5, className)} {...props} />
)

export const P = ({ children, ...props }) => {
    const dontWrap = ['figure']
    if (
        !Array.isArray(children) &&
        !isString(children) &&
        children.hasOwnProperty('type') &&
        dontWrap.includes(children.type)
    ) {
        return children
    }
    return <p {...props}>{children}</p>
}

export const Abbr = ({ title, children }) => (
    <abbr
        className={classes.abbr}
        data-tooltip={title}
        data-tooltip-style="code"
        aria-label={title}
    >
        {children}
    </abbr>
)

export const Label = ({ className, ...props }) => (
    <span className={classNames(classes.label, className)} {...props} />
)

export const InlineList = ({ Component = 'p', gutterBottom = true, className, children }) => {
    const listClassNames = classNames(classes['inline-list'], className, {
        [classes['no-gutter']]: !gutterBottom,
    })
    return <Component className={listClassNames}>{children}</Component>
}

export const Help = ({ children, className, size = 16 }) => (
    <span className={classNames(classes.help, className)} data-tooltip={children}>
        <Icon name="help2" width={size} />
    </span>
)

const Permalink = ({ id, children }) =>
    !id ? (
        <span className={headingTextClassName}>{children}</span>
    ) : (
        <a href={`#${id}`} className={classNames(headingTextClassName, classes.permalink)}>
            {children}
        </a>
    )

const Headline = ({
    Component,
    id,
    name,
    version,
    model,
    tag,
    source,
    hidden,
    action,
    permalink = true,
    className,
    children,
}) => {
    // This can be set via hidden="true" and as a prop, so we need to accept both
    if (hidden === true || hidden === 'true') return null
    const hasAction = !!source || !!action
    const headingClassNames = classNames(classes.heading, className, {
        [classes.clear]: hasAction,
    })
    const tags = tag ? tag.split(',').map((t) => t.trim()) : []
    return (
        <Component id={id} name={name} className={headingClassNames}>
            <Permalink id={permalink ? id : null}>{children} </Permalink>
            {tags.map((tag, i) => (
                <Tag spaced key={i}>
                    {tag}
                </Tag>
            ))}
            {version && (
                <Tag spaced variant="new">
                    {version}
                </Tag>
            )}
            {model && (
                <Tag spaced variant="model">
                    {model}
                </Tag>
            )}

            {hasAction && (
                <div className={classes.action}>
                    {source && (
                        <Button icon="code" to={github(source)}>
                            Source
                        </Button>
                    )}
                    {action}
                </div>
            )}
        </Component>
    )
}

Headline.propTypes = {
    Component: PropTypes.oneOfType([PropTypes.element, PropTypes.string]).isRequired,
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.oneOf([false])]),
    version: PropTypes.string,
    model: PropTypes.string,
    source: PropTypes.string,
    tag: PropTypes.string,
    hidden: PropTypes.oneOfType([PropTypes.bool, PropTypes.oneOf(['true', 'false'])]),
    action: PropTypes.node,
    className: PropTypes.string,
}

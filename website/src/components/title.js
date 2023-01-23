import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'

import Button from './button'
import Tag from './tag'
import { OptionalLink } from './link'
import { InlineCode } from './code'
import { H1, Label, InlineList, Help } from './typography'
import Icon from './icon'

import classes from '../styles/title.module.sass'

const MetaItem = ({ label, url, children, help }) => (
    <span>
        <Label className={classes.label}>{label}:</Label>
        <OptionalLink to={url}>{children}</OptionalLink>
        {help && (
            <>
                {' '}
                <Help>{help}</Help>
            </>
        )}
    </span>
)

export default function Title({
    id,
    title,
    tag,
    version,
    teaser,
    source,
    image,
    apiDetails,
    children,
    ...props
}) {
    const hasApiDetails = Object.values(apiDetails || {}).some(v => v)
    const metaIconProps = { className: classes.metaIcon, width: 18 }
    return (
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
            {(tag || version) && (
                <div className={classes.tags}>
                    {tag && <Tag spaced>{tag}</Tag>}
                    {version && (
                        <Tag variant="new" spaced>
                            {version}
                        </Tag>
                    )}
                </div>
            )}

            {hasApiDetails && (
                <InlineList Component="div" className={classes.teaser}>
                    {apiDetails.stringName && (
                        <MetaItem
                            label="String name"
                            //help="String name of the component to use with nlp.add_pipe"
                        >
                            <InlineCode>{apiDetails.stringName}</InlineCode>
                        </MetaItem>
                    )}
                    {apiDetails.baseClass && (
                        <MetaItem label="Base class" url={apiDetails.baseClass.slug}>
                            <InlineCode>{apiDetails.baseClass.title}</InlineCode>
                        </MetaItem>
                    )}
                    {apiDetails.trainable != null && (
                        <MetaItem label="Trainable">
                            <span aria-label={apiDetails.trainable ? 'yes' : 'no'}>
                                {apiDetails.trainable ? (
                                    <Icon name="yes" variant="success" {...metaIconProps} />
                                ) : (
                                    <Icon name="no" {...metaIconProps} />
                                )}
                            </span>
                        </MetaItem>
                    )}
                </InlineList>
            )}
            {teaser && <div className={classNames('heading-teaser', classes.teaser)}>{teaser}</div>}
            {children}
        </header>
    )
}

Title.propTypes = {
    title: PropTypes.string,
    tag: PropTypes.string,
    teaser: PropTypes.node,
    source: PropTypes.string,
    image: PropTypes.string,
    children: PropTypes.node,
}

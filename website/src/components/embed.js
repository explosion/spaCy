import React, { Fragment } from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'

import Link from './link'
import { InlineCode } from './code'
import { markdownToReact } from './util'

import classes from '../styles/embed.module.sass'

const YouTube = ({ id, ratio = '16x9', className }) => {
    const embedClassNames = classNames(classes.root, classes.responsive, className, {
        [classes.ratio16x9]: ratio === '16x9',
        [classes.ratio4x3]: ratio === '4x3',
    })
    const url = `https://www.youtube-nocookie.com/embed/${id}`
    return (
        <figure className={embedClassNames}>
            <iframe
                className={classes.iframe}
                title={id}
                src={url}
                frameBorder={0}
                height={500}
                allowFullScreen
            />
        </figure>
    )
}

YouTube.propTypes = {
    id: PropTypes.string.isRequired,
    ratio: PropTypes.oneOf(['16x9', '4x3']),
}

const SoundCloud = ({ id, color = '09a3d5', title }) => {
    const url = `https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/${id}&color=%23${color}&auto_play=false&hide_related=false&show_comments=true&show_user=true&show_reposts=false&show_teaser=true`
    return (
        <figure className={classes.root}>
            <iframe
                title={title}
                width="100%"
                height={166}
                scrolling="no"
                frameborder="no"
                allow="autoplay"
                src={url}
            />
        </figure>
    )
}

SoundCloud.propTypes = {
    id: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    color: PropTypes.string,
}

function formatHTML(html) {
    const encoded = encodeURIComponent(html)
    return `<html><head><meta charset="UTF-8"></head><body>${encoded}</body></html>`
}

const Iframe = ({ title, src, html, width = 800, height = 300 }) => {
    const source = html ? `data:text/html,${formatHTML(html)}` : src
    return (
        <iframe
            className={classes.standalone}
            title={title}
            src={source}
            width={width}
            height={height}
            allowFullScreen
            frameBorder="0"
        />
    )
}

Iframe.propTypes = {
    title: PropTypes.string.isRequired,
    src: PropTypes.string,
    html: PropTypes.string,
    width: PropTypes.number,
    height: PropTypes.number,
}

const Image = ({ src, alt, title, ...props }) => {
    // This is only needed for image types that are NOT handled by
    // gatsby-remark-images, i.e. mostly SVGs. The plugin adds formatting
    // and support for captions, so this normalises that behaviour.
    const linkClassNames = classNames('gatsby-resp-image-link', classes.imageLink)
    const markdownComponents = { code: InlineCode, p: Fragment, a: Link }
    return (
        <figure className="gatsby-resp-image-figure">
            <Link className={linkClassNames} href={src} hidden forceExternal>
                <img className={classes.image} src={src} alt={alt} width={650} height="auto" />
            </Link>
            {title && (
                <figcaption className="gatsby-resp-image-figcaption">
                    {markdownToReact(title, markdownComponents)}
                </figcaption>
            )}
        </figure>
    )
}

export { YouTube, SoundCloud, Iframe, Image }

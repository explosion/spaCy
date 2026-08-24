import React, { Fragment } from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import ImageNext from 'next/image'

import Link from './link'
import Button from './button'
import { InlineCode } from './inlineCode'
import MarkdownToReact from './markdownToReactDynamic'

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

const Iframe = ({ title, src, width = 800, height = 300 }) => {
    return (
        <iframe
            className={classes.standalone}
            title={title}
            src={src}
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

// Raster images are served through the Netlify Image CDN, which resizes them to
// the width they're actually displayed at and negotiates a modern format
// (WebP/AVIF) based on the request's Accept header. SVGs are skipped: they're
// tiny once Brotli-compressed and would only get rasterised. Animated GIFs are
// skipped too, since the Image CDN passes them through unchanged.
const OPTIMIZABLE_IMAGE = /\.(jpe?g|png)$/i

const imageCdnUrl = (src, width) =>
    `/.netlify/images?url=${encodeURIComponent(src)}&w=${width}&fit=contain`

// Returns the `src`/`srcSet` pair for an image displayed at `width` CSS pixels.
// Local rasters get a 1x/2x srcSet off the Image CDN; anything else (SVG, GIF,
// remote or data URLs) is passed through untouched.
const imageSourceProps = (src, width) => {
    const isLocalRaster =
        typeof src === 'string' && src.startsWith('/') && OPTIMIZABLE_IMAGE.test(src.split('?')[0])
    if (!isLocalRaster || !width) return { src }
    return {
        src: imageCdnUrl(src, width),
        srcSet: `${imageCdnUrl(src, width)} 1x, ${imageCdnUrl(src, width * 2)} 2x`,
    }
}

const Image = ({ src, alt, title, href, ...props }) => {
    // This is only needed for image types that are NOT handled by
    // gatsby-remark-images, i.e. mostly SVGs. The plugin adds formatting
    // and support for captions, so this normalises that behaviour.
    const linkClassNames = classNames('gatsby-resp-image-link', classes['image-link'])
    const markdownComponents = { code: InlineCode, p: Fragment, a: Link }
    return (
        <figure className="gatsby-resp-image-figure">
            {href ? (
                <Link className={linkClassNames} href={href} noLinkLayout forceExternal>
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                        className={classes.image}
                        {...imageSourceProps(src, 650)}
                        alt={alt}
                        width={650}
                        height="auto"
                        loading="lazy"
                        decoding="async"
                    />
                </Link>
            ) : (
                /* eslint-disable-next-line @next/next/no-img-element */
                <img
                    className={classes.image}
                    {...imageSourceProps(src, 650)}
                    alt={alt}
                    width={650}
                    height="auto"
                    loading="lazy"
                    decoding="async"
                />
            )}

            {title && (
                <figcaption className="gatsby-resp-image-figcaption">
                    <MarkdownToReact markdown={title} />
                </figcaption>
            )}
        </figure>
    )
}

const ImageScrollable = ({ src, alt, width, ...props }) => {
    return (
        <figure className={classNames(classes.standalone, classes.scrollable)}>
            <img
                className={classes['image-scrollable']}
                {...imageSourceProps(src, width)}
                alt={alt}
                width={width}
                height="auto"
                loading="lazy"
                decoding="async"
            />
        </figure>
    )
}

const Standalone = ({ height, children, ...props }) => {
    return (
        <figure className={classes.standalone} style={{ height }}>
            {children}
        </figure>
    )
}

const ImageFill = ({ image, ...props }) => {
    // `next/image` runs with `unoptimized`, so it emits `src` verbatim — point it
    // at the Image CDN to get a resized, format-negotiated version. Only `src` is
    // set (no `srcSet`): next/image owns that attribute.
    return (
        <span
            className={classes['figure-fill']}
            style={{ paddingBottom: `${(image.height / image.width) * 100}%` }}
        >
            <ImageNext src={imageSourceProps(image.src, 1400).src} {...props} fill />
        </span>
    )
}

const GoogleSheet = ({ id, link, height, button = 'View full table' }) => {
    return (
        <figure className={classes.root}>
            <iframe
                title={id}
                scrolling="no"
                className={classes['google-sheet']}
                height={height}
                src={`https://docs.google.com/spreadsheets/d/e/${id}/pubhtml?widget=true&amp;headers=false`}
            />
            {link && (
                <Button href={`https://docs.google.com/spreadsheets/d/${link}/view`}>
                    {button}
                </Button>
            )}
        </figure>
    )
}

export { YouTube, SoundCloud, Iframe, Image, ImageFill, ImageScrollable, GoogleSheet, Standalone }

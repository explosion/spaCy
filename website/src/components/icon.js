import React, { Fragment } from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import SVG from 'react-inlinesvg'

import gitHubIcon from '../images/icons/github.svg'
import twitterIcon from '../images/icons/twitter.svg'
import websiteIcon from '../images/icons/website.svg'
import warningIcon from '../images/icons/warning.svg'
import infoIcon from '../images/icons/info.svg'
import acceptIcon from '../images/icons/accept.svg'
import rejectIcon from '../images/icons/reject.svg'
import docsIcon from '../images/icons/docs.svg'
import codeIcon from '../images/icons/code.svg'
import helpIcon from '../images/icons/help.svg'
import helpOutlineIcon from '../images/icons/help-outline.svg'
import arrowRightIcon from '../images/icons/arrow-right.svg'
import yesIcon from '../images/icons/yes.svg'
import noIcon from '../images/icons/no.svg'
import neutralIcon from '../images/icons/neutral.svg'
import offlineIcon from '../images/icons/offline.svg'
import searchIcon from '../images/icons/search.svg'
import moonIcon from '../images/icons/moon.svg'
import clipboardIcon from '../images/icons/clipboard.svg'
import networkIcon from '../images/icons/network.svg'
import downloadIcon from '../images/icons/download.svg'
import packageIcon from '../images/icons/package.svg'

import { isString } from './util'
import classes from '../styles/icon.module.sass'

const icons = {
    github: gitHubIcon,
    twitter: twitterIcon,
    website: websiteIcon,
    warning: warningIcon,
    danger: infoIcon,
    info: infoIcon,
    accept: acceptIcon,
    reject: rejectIcon,
    docs: docsIcon,
    code: codeIcon,
    help: helpIcon,
    help2: helpOutlineIcon,
    arrowright: arrowRightIcon,
    yes: yesIcon,
    no: noIcon,
    neutral: neutralIcon,
    offline: offlineIcon,
    search: searchIcon,
    moon: moonIcon,
    clipboard: clipboardIcon,
    network: networkIcon,
    download: downloadIcon,
    package: packageIcon,
}

export default function Icon({
    name,
    width = 20,
    height,
    inline = false,
    variant,
    className,
    ...props
}) {
    const icon = icons[name]
    const iconClassNames = classNames(classes.root, className, {
        [classes.inline]: inline,
        [classes.success]: variant === 'success',
        [classes.error]: variant === 'error',
        [classes.subtle]: variant === 'subtle',
    })
    return !icon ? null : (
        <SVG
            src={icon.src}
            className={iconClassNames}
            aria-hidden="true"
            width={width}
            height={height || width}
            {...props}
        />
    )
}

Icon.propTypes = {
    name: PropTypes.oneOf(Object.keys(icons)),
    width: PropTypes.number,
    height: PropTypes.number,
    inline: PropTypes.bool,
    variant: PropTypes.oneOf(['success', 'error', 'subtle']),
    className: PropTypes.string,
}

export function replaceEmoji(cellChildren) {
    const icons = {
        '✅': { name: 'yes', variant: 'success', 'aria-label': 'positive' },
        '❌': { name: 'no', variant: 'error', 'aria-label': 'negative' },
    }
    const iconRe = new RegExp(`^(${Object.keys(icons).join('|')})`, 'g')
    let children = isString(cellChildren) ? [cellChildren] : cellChildren
    let hasIcon = false
    if (Array.isArray(children)) {
        children = children.map((child, i) => {
            if (isString(child)) {
                const icon = icons[child.trim()]
                if (icon) {
                    hasIcon = true
                    return (
                        <Icon
                            {...icon}
                            inline={i < children.length}
                            aria-hidden={undefined}
                            key={i}
                        />
                    )
                } else if (iconRe.test(child)) {
                    hasIcon = true
                    const [, iconName, text] = child.split(iconRe)
                    return (
                        <Fragment key={i}>
                            <Icon {...icons[iconName]} aria-hidden={undefined} inline={true} />
                            {text.replace(/^\s+/g, '')}
                        </Fragment>
                    )
                }
                // Work around prettier auto-escape
                if (child.startsWith('\\')) return child.slice(1)
            }
            return child
        })
    }
    return { content: children, hasIcon }
}

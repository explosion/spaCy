import React, { Fragment } from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'

import GitHubIcon from '-!svg-react-loader!../images/icons/github.svg'
import TwitterIcon from '-!svg-react-loader!../images/icons/twitter.svg'
import WebsiteIcon from '-!svg-react-loader!../images/icons/website.svg'
import WarningIcon from '-!svg-react-loader!../images/icons/warning.svg'
import InfoIcon from '-!svg-react-loader!../images/icons/info.svg'
import AcceptIcon from '-!svg-react-loader!../images/icons/accept.svg'
import RejectIcon from '-!svg-react-loader!../images/icons/reject.svg'
import DocsIcon from '-!svg-react-loader!../images/icons/docs.svg'
import CodeIcon from '-!svg-react-loader!../images/icons/code.svg'
import HelpIcon from '-!svg-react-loader!../images/icons/help.svg'
import HelpOutlineIcon from '-!svg-react-loader!../images/icons/help-outline.svg'
import ArrowRightIcon from '-!svg-react-loader!../images/icons/arrow-right.svg'
import YesIcon from '-!svg-react-loader!../images/icons/yes.svg'
import NoIcon from '-!svg-react-loader!../images/icons/no.svg'
import NeutralIcon from '-!svg-react-loader!../images/icons/neutral.svg'
import OfflineIcon from '-!svg-react-loader!../images/icons/offline.svg'
import SearchIcon from '-!svg-react-loader!../images/icons/search.svg'
import MoonIcon from '-!svg-react-loader!../images/icons/moon.svg'
import ClipboardIcon from '-!svg-react-loader!../images/icons/clipboard.svg'
import NetworkIcon from '-!svg-react-loader!../images/icons/network.svg'
import DownloadIcon from '-!svg-react-loader!../images/icons/download.svg'
import PackageIcon from '-!svg-react-loader!../images/icons/package.svg'

import { isString } from './util'
import classes from '../styles/icon.module.sass'

const icons = {
    github: GitHubIcon,
    twitter: TwitterIcon,
    website: WebsiteIcon,
    warning: WarningIcon,
    danger: InfoIcon,
    info: InfoIcon,
    accept: AcceptIcon,
    reject: RejectIcon,
    docs: DocsIcon,
    code: CodeIcon,
    help: HelpIcon,
    help2: HelpOutlineIcon,
    arrowright: ArrowRightIcon,
    yes: YesIcon,
    no: NoIcon,
    neutral: NeutralIcon,
    offline: OfflineIcon,
    search: SearchIcon,
    moon: MoonIcon,
    clipboard: ClipboardIcon,
    network: NetworkIcon,
    download: DownloadIcon,
    package: PackageIcon,
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
    const IconComponent = icons[name]
    const iconClassNames = classNames(classes.root, className, {
        [classes.inline]: inline,
        [classes.success]: variant === 'success',
        [classes.error]: variant === 'error',
        [classes.subtle]: variant === 'subtle',
    })
    return !IconComponent ? null : (
        <IconComponent
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

import React from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'

import { ReactComponent as GitHubIcon } from '../images/icons/github.svg'
import { ReactComponent as TwitterIcon } from '../images/icons/twitter.svg'
import { ReactComponent as WebsiteIcon } from '../images/icons/website.svg'
import { ReactComponent as WarningIcon } from '../images/icons/warning.svg'
import { ReactComponent as InfoIcon } from '../images/icons/info.svg'
import { ReactComponent as AcceptIcon } from '../images/icons/accept.svg'
import { ReactComponent as RejectIcon } from '../images/icons/reject.svg'
import { ReactComponent as DocsIcon } from '../images/icons/docs.svg'
import { ReactComponent as CodeIcon } from '../images/icons/code.svg'
import { ReactComponent as HelpIcon } from '../images/icons/help.svg'
import { ReactComponent as HelpOutlineIcon } from '../images/icons/help-outline.svg'
import { ReactComponent as ArrowRightIcon } from '../images/icons/arrow-right.svg'
import { ReactComponent as YesIcon } from '../images/icons/yes.svg'
import { ReactComponent as NoIcon } from '../images/icons/no.svg'
import { ReactComponent as NeutralIcon } from '../images/icons/neutral.svg'
import { ReactComponent as OfflineIcon } from '../images/icons/offline.svg'
import { ReactComponent as SearchIcon } from '../images/icons/search.svg'
import { ReactComponent as MoonIcon } from '../images/icons/moon.svg'
import { ReactComponent as ClipboardIcon } from '../images/icons/clipboard.svg'
import { ReactComponent as NetworkIcon } from '../images/icons/network.svg'
import { ReactComponent as DownloadIcon } from '../images/icons/download.svg'
import { ReactComponent as PackageIcon } from '../images/icons/package.svg'

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

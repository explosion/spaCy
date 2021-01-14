import React from 'react'
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
}

const Icon = ({ name, width, height, inline, variant, className }) => {
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
        />
    )
}

Icon.defaultProps = {
    width: 20,
    inline: false,
}

Icon.propTypes = {
    name: PropTypes.oneOf(Object.keys(icons)),
    width: PropTypes.number,
    height: PropTypes.number,
    inline: PropTypes.bool,
    variant: PropTypes.oneOf(['success', 'error', 'subtle']),
    className: PropTypes.string,
}

export default Icon

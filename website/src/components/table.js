import React from 'react'
import classNames from 'classnames'

import Icon from './icon'
import { isString } from './util'
import classes from '../styles/table.module.sass'

function isNum(children) {
    return isString(children) && /^\d+[.,]?[\dx]+?(|x|ms|mb|gb|k|m)?$/i.test(children)
}

function getCellContent(children) {
    const icons = {
        '✅': { name: 'yes', variant: 'success' },
        '❌': { name: 'no', variant: 'error' },
    }

    if (isString(children) && icons[children.trim()]) {
        const iconProps = icons[children.trim()]
        return <Icon {...iconProps} />
    }
    // Work around prettier auto-escape
    if (isString(children) && children.startsWith('\\')) {
        return children.slice(1)
    }
    return children
}

function isFootRow(children) {
    const rowRegex = /^(RETURNS|YIELDS|CREATES|PRINTS)/
    if (children.length && children[0].props.name === 'td') {
        const cellChildren = children[0].props.children
        if (
            cellChildren &&
            cellChildren.props &&
            cellChildren.props.children &&
            isString(cellChildren.props.children)
        ) {
            return rowRegex.test(cellChildren.props.children)
        }
    }
    return false
}

export const Table = props => <table className={classes.root} {...props} />
export const Th = props => <th className={classes.th} {...props} />

export const Tr = ({ children, ...props }) => {
    const foot = isFootRow(children)
    const trClasssNames = classNames(classes.tr, {
        [classes.footer]: foot,
        'table-footer': foot,
    })

    return (
        <tr className={trClasssNames} {...props}>
            {children}
        </tr>
    )
}

export const Td = ({ num, nowrap, className, children, ...props }) => {
    const content = getCellContent(children)
    const tdClassNames = classNames(classes.td, className, {
        [classes.num]: num || isNum(children),
        [classes.nowrap]: nowrap,
    })
    return (
        <td className={tdClassNames} {...props}>
            {content}
        </td>
    )
}

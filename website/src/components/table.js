import React, { Fragment } from 'react'
import classNames from 'classnames'

import Icon from './icon'
import { Help } from './typography'
import { isString } from './util'
import classes from '../styles/table.module.sass'

const FOOT_ROW_REGEX = /^(RETURNS|YIELDS|CREATES|PRINTS|EXECUTES|UPLOADS|DOWNLOADS)/

function isNum(children) {
    return isString(children) && /^\d+[.,]?[\dx]+?(|x|ms|mb|gb|k|m)?$/i.test(children)
}

function getCellContent(cellChildren) {
    const icons = {
        '✅': { name: 'yes', variant: 'success', 'aria-label': 'positive' },
        '❌': { name: 'no', variant: 'error', 'aria-label': 'negative' },
    }
    const iconRe = new RegExp(`^(${Object.keys(icons).join('|')})`, 'g')
    let children = isString(cellChildren) ? [cellChildren] : cellChildren
    if (Array.isArray(children)) {
        return children.map((child, i) => {
            if (isString(child)) {
                const icon = icons[child.trim()]
                const props = {
                    inline: i < children.length,
                    'aria-hidden': undefined,
                }
                if (icon) {
                    return <Icon {...icon} {...props} key={i} />
                } else if (iconRe.test(child)) {
                    const [, iconName, text] = child.split(iconRe)
                    return (
                        <Fragment key={i}>
                            <Icon {...icons[iconName]} {...props} />
                            {text.trim()}
                        </Fragment>
                    )
                }
                // Work around prettier auto-escape
                if (child.startsWith('\\')) return child.slice(1)
            }
            return child
        })
    }
    return children
}

function isDividerRow(children) {
    if (children.length && children[0].props && children[0].props.name == 'td') {
        const tdChildren = children[0].props.children
        if (tdChildren && !Array.isArray(tdChildren) && tdChildren.props) {
            return tdChildren.props.name === 'em'
        }
    }
    return false
}

function isFootRow(children) {
    if (children.length && children[0].props.name === 'td') {
        const cellChildren = children[0].props.children
        if (
            cellChildren &&
            cellChildren.props &&
            cellChildren.props.children &&
            isString(cellChildren.props.children)
        ) {
            return FOOT_ROW_REGEX.test(cellChildren.props.children)
        }
    }
    return false
}

export const Table = ({ fixed, className, ...props }) => {
    const tableClassNames = classNames(classes.root, className, {
        [classes.fixed]: fixed,
    })
    return <table className={tableClassNames} {...props} />
}

export const Th = ({ children, ...props }) => {
    const isRotated = children && !isString(children) && children.type && children.type.name == 'Tx'
    const thClassNames = classNames(classes.th, { [classes.thRotated]: isRotated })
    return (
        <th className={thClassNames} {...props}>
            {children}
        </th>
    )
}

// Rotated head, child of Th
export const Tx = ({ children, ...props }) => (
    <div className={classes.tx} {...props}>
        <span>{children}</span>
    </div>
)

export const Tr = ({ evenodd = true, children, ...props }) => {
    const foot = isFootRow(children)
    const isDivider = isDividerRow(children)
    const trClasssNames = classNames({
        [classes.tr]: evenodd,
        [classes.footer]: foot,
        [classes.divider]: isDivider,
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

import React from 'react'
import classNames from 'classnames'

import classes from '../styles/list.module.sass'
import { replaceEmoji } from './icon'

export const Ol = props => <ol className={classes.ol} {...props} />
export const Ul = props => <ul className={classes.ul} {...props} />
export const Li = ({ children, emoji, ...props }) => {
    const { hasIcon, content } = replaceEmoji(children)
    const liClassNames = classNames(classes.li, {
        [classes.liIcon]: hasIcon,
        [classes.emoji]: emoji,
    })
    return (
        <li data-emoji={emoji} className={liClassNames} {...props}>
            {content}
        </li>
    )
}

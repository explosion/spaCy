import React from 'react'
import { Code } from './code'
import classes from '../styles/code.module.sass'

export const Pre = (props) => {
    return <pre className={classes['pre']}>{props.children}</pre>
}

const CodeBlock = (props) => (
    <Pre>
        <Code {...props} />
    </Pre>
)
export default CodeBlock

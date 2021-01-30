import React, { useState, useRef } from 'react'

import Icon from './icon'
import classes from '../styles/copy.module.sass'

export function copyToClipboard(ref, callback) {
    const isClient = typeof window !== 'undefined'
    if (ref.current && isClient) {
        ref.current.select()
        document.execCommand('copy')
        callback(true)
        ref.current.blur()
        setTimeout(() => callback(false), 1000)
    }
}

export default function CopyInput({ text, prefix }) {
    const isClient = typeof window !== 'undefined'
    const supportsCopy = isClient && document.queryCommandSupported('copy')
    const textareaRef = useRef()
    const [copySuccess, setCopySuccess] = useState(false)
    const onClick = () => copyToClipboard(textareaRef, setCopySuccess)

    function selectText() {
        if (textareaRef.current && isClient) {
            textareaRef.current.select()
        }
    }

    return (
        <div className={classes.root}>
            {prefix && <span className={classes.prefix}>{prefix}</span>}
            <textarea
                ref={textareaRef}
                readOnly
                className={classes.textarea}
                defaultValue={text}
                rows={1}
                onClick={selectText}
            />
            {supportsCopy && (
                <button title="Copy to clipboard" onClick={onClick}>
                    <Icon width={16} name={copySuccess ? 'accept' : 'clipboard'} />
                </button>
            )}
        </div>
    )
}

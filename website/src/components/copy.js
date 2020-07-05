import React, { useState, useRef } from 'react'

import Icon from './icon'
import classes from '../styles/copy.module.sass'

const CopyInput = ({ text, prefix }) => {
    const isClient = typeof window !== 'undefined'
    const supportsCopy = isClient && document.queryCommandSupported('copy')
    const textareaRef = useRef()
    const [copySuccess, setCopySuccess] = useState(false)

    function copyToClipboard() {
        if (textareaRef.current && isClient) {
            textareaRef.current.select()
            document.execCommand('copy')
            setCopySuccess(true)
            textareaRef.current.blur()
            setTimeout(() => setCopySuccess(false), 1000)
        }
    }

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
                <button title="Copy to clipboard" onClick={copyToClipboard}>
                    <Icon width={16} name={copySuccess ? 'accept' : 'clipboard'} />
                </button>
            )}
        </div>
    )
}

export default CopyInput

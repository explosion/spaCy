import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import classNames from 'classnames'
import highlightCode from 'gatsby-remark-prismjs/highlight-code.js'

import Icon from './icon'
import Link from './link'
import classes from '../styles/code.module.sass'

const defaultErrorMsg = `Can't fetch code example from GitHub :(

Please use the link below to view the example. If you've come across
a broken link, we always appreciate a pull request to the repository,
or a report on the issue tracker. Thanks!`

const GitHubCode = ({ url, lang, errorMsg = defaultErrorMsg, className }) => {
    const [initialized, setInitialized] = useState(false)
    const [code, setCode] = useState(errorMsg)
    const codeClassNames = classNames(classes.code, classes.maxHeight, className)

    const rawUrl = url
        .replace('github.com', 'raw.githubusercontent.com')
        .replace('/blob', '')
        .replace('/tree', '')

    useEffect(() => {
        if (!initialized) {
            setCode(null)
            fetch(rawUrl)
                .then(res => res.text().then(text => ({ text, ok: res.ok })))
                .then(({ text, ok }) => {
                    setCode(ok ? text : errorMsg)
                })
                .catch(err => {
                    setCode(errorMsg)
                    console.error(err)
                })
            setInitialized(true)
        }
    }, [initialized, rawUrl, errorMsg])

    const highlighted = lang === 'none' || !code ? code : highlightCode(lang, code)

    return (
        <>
            <header className={classes.header}>
                <Link to={url} hidden>
                    <Icon name="github" width={16} inline />
                    <code className={classNames(classes.inlineCode, classes.inlineCodeDark)}>
                        {rawUrl.split('.com/')[1]}
                    </code>
                </Link>
            </header>
            <code className={codeClassNames} dangerouslySetInnerHTML={{ __html: highlighted }} />
        </>
    )
}

GitHubCode.propTypes = {
    url: PropTypes.string.isRequired,
    lang: PropTypes.string,
    errorMsg: PropTypes.string,
    className: PropTypes.string,
}

export default React.memo(GitHubCode)

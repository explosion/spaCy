import React, { useEffect, useState } from 'react'
import PropTypes from 'prop-types'
import { window } from 'browser-monads'

import Icon from './icon'
import * as classes from '../styles/search.module.sass'

export default function Search({ id = 'docsearch', placeholder = 'Search docs', settings = {} }) {
    const { apiKey, indexName, appId } = settings
    const [initialized, setInitialized] = useState(false)
    useEffect(() => {
        if (!initialized) {
            setInitialized(true)
            // window.docsearch({
            //     appId,
            //     apiKey,
            //     indexName,
            //     inputSelector: `#${id}`,
            //     debug: false,
            // })
        }
    }, [initialized, apiKey, indexName, id])
    if (!apiKey && !indexName) return null
    return (
        <form className={classes.root}>
            {/* <label htmlFor={id} className={classes.icon}>
                <Icon name="search" width={20} />
            </label>
            <input
                id={id}
                className={classes.input}
                type="search"
                placeholder={placeholder}
                aria-label={placeholder}
            /> */}
        </form>
    )
}

Search.propTypes = {
    settings: PropTypes.shape({
        apiKey: PropTypes.string.isRequired,
        indexName: PropTypes.string.isRequired,
    }).isRequired,
    id: PropTypes.string,
    placeholder: PropTypes.string,
}

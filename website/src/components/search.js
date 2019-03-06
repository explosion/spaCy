import React, { useEffect, useState } from 'react'
import PropTypes from 'prop-types'
import { window } from 'browser-monads'

import Icon from './icon'
import classes from '../styles/search.module.sass'

const Search = ({ id, placeholder, settings }) => {
    const { apiKey, indexName } = settings
    const [isInitialized, setIsInitialized] = useState(false)
    useEffect(() => {
        if (!isInitialized) {
            setIsInitialized(true)
            window.docsearch({
                apiKey,
                indexName,
                inputSelector: `#${id}`,
                debug: false,
            })
        }
    }, window.docsearch)
    return (
        <form className={classes.root}>
            <label htmlFor={id} className={classes.icon}>
                <Icon name="search" width={20} />
            </label>
            <input
                id={id}
                className={classes.input}
                type="search"
                placeholder={placeholder}
                aria-label={placeholder}
            />
        </form>
    )
}

Search.defaultProps = {
    id: 'docsearch',
    placeholder: 'Search docs',
    settings: {},
}

Search.propTypes = {
    settings: PropTypes.shape({
        apiKey: PropTypes.string.isRequired,
        indexName: PropTypes.string.isRequired,
    }).isRequired,
    id: PropTypes.string.isRequired,
    placeholder: PropTypes.string.isRequired,
}

export default Search

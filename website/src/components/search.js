import React, { useEffect, useState } from 'react'
import PropTypes from 'prop-types'
import { DocSearch } from '@docsearch/react'
import '@docsearch/css'

import siteMetadata from '../../meta/site.json'

export default function Search({ placeholder = 'Search docs' }) {
    const { apiKey, indexName, appId } = siteMetadata.docSearch
    return (
        <DocSearch appId={appId} indexName={indexName} apiKey={apiKey} placeholder={placeholder} />
    )
}

Search.propTypes = {
    id: PropTypes.string,
    placeholder: PropTypes.string,
}

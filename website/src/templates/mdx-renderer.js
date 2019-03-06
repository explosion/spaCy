/**
 * Temporary hack to prevent this issue:
 * https://github.com/ChristopherBiscardi/gatsby-mdx/issues/244
 */

import React from 'react'
import { MDXTag } from '@mdx-js/tag'
import { withMDXComponents } from '@mdx-js/tag/dist/mdx-provider'
import { withMDXScope } from 'gatsby-mdx/context'

const WrappedComponent = React.memo(({ scope = {}, components = {}, children, ...props }) => {
    if (!children) return null
    const fullScope = { React, MDXTag, ...scope }
    const keys = Object.keys(fullScope)
    const values = keys.map(key => fullScope[key])
    const fn = new Function('_fn', ...keys, `${children}`) // eslint-disable-line no-new-func
    const End = fn({}, ...values)
    return React.createElement(End, { components, ...props })
})

export default withMDXScope(withMDXComponents(WrappedComponent))

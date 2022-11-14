import remarkGfm from 'remark-gfm'
import remarkUnwrapImages from 'remark-unwrap-images'

import remarkCustomAttrs from './remarkCustomAttrs.mjs'
import remarkWrapSections from './remarkWrapSections.mjs'

const remarkPlugins = [
    remarkGfm,
    remarkUnwrapImages,
    remarkCustomAttrs,
    remarkWrapSections,
]

export default remarkPlugins

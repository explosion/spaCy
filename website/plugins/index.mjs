import remarkGfm from 'remark-gfm'

import remarkCustomAttrs from './remarkCustomAttrs.mjs'
import remarkWrapSections from './remarkWrapSections.mjs'

const remarkPlugins = [
    remarkGfm,
    remarkCustomAttrs,
    remarkWrapSections,
]

export default remarkPlugins

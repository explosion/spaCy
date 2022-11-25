import remarkGfm from 'remark-gfm'
import remarkUnwrapImages from 'remark-unwrap-images'

import remarkCustomAttrs from './remarkCustomAttrs.mjs'
import remarkWrapSections from './remarkWrapSections.mjs'
import remarkCodeBlocks from './remarkCodeBlocks.mjs'

const remarkPlugins = [
    remarkGfm,
    remarkUnwrapImages,
    remarkCustomAttrs,
    remarkCodeBlocks,
    remarkWrapSections,
]

export default remarkPlugins

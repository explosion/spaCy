import remarkGfm from 'remark-gfm'
import remarkUnwrapImages from 'remark-unwrap-images'

import remarkCustomAttrs from './remarkCustomAttrs.mjs'
import remarkWrapSections from './remarkWrapSections.mjs'
import remarkCodeBlocks from './remarkCodeBlocks.mjs'
import remarkFindAndReplace from './remarkFindAndReplace.mjs'

const remarkPlugins = [
    remarkGfm,
    remarkFindAndReplace,
    remarkUnwrapImages,
    remarkCustomAttrs,
    remarkCodeBlocks,
    remarkWrapSections,
]

export default remarkPlugins

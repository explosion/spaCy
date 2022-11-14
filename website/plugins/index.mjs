import remarkGfm from 'remark-gfm'
import remarkUnwrapImages from 'remark-unwrap-images'

import remarkCustomAttrs from './remarkCustomAttrs.mjs'

const remarkPlugins = [remarkGfm, remarkUnwrapImages, remarkCustomAttrs]

export default remarkPlugins

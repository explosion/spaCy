import remarkGfm from 'remark-gfm'

import remarkCustomAttrs from './remarkCustomAttrs.mjs'

const remarkPlugins = [remarkGfm, remarkCustomAttrs]

export default remarkPlugins

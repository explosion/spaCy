/**
 * Simplified implementation of remark-attr that allows custom attributes on
 * nodes *inline* via the following syntax: {#some-id key="value"}. Extracting
 * them inline is slightly hackier (at least in this implementation), but it
 * makes the resulting markup valid and compatible with formatters like
 * Prettier, which do not allow additional content right below headlines.
 * Based on: https://github.com/arobase-che/remark-attr
 */

const visit = require('unist-util-visit')
const parseAttr = require('md-attr-parser')

const defaultOptions = {
    elements: ['heading', 'link'],
}

function remarkCustomAttrs(userOptions = {}) {
    const options = Object.assign({}, defaultOptions, userOptions)
    function transformer(tree) {
        visit(tree, null, node => {
            if (options.elements.includes(node.type)) {
                if (
                    node.children &&
                    node.children.length &&
                    node.children[0].type === 'text' &&
                    node.children[0].value
                ) {
                    if (node.children.length > 1 && node.children.every(el => el.type === 'text')) {
                        // If headlines contain escaped characters, e.g.
                        // Doc.\_\_init\_\_, it will be split into several nodes
                        const mergedText = node.children.map(el => el.value).join('')
                        node.children[0].value = mergedText
                        node.children = [node.children[0]]
                    }
                    const parsed = node.children[0].value.split(/\{(.*?)\}/)
                    if (parsed.length >= 2 && parsed[1]) {
                        const text = parsed[0].trim()
                        const { prop } = parseAttr(parsed[1])
                        const data = node.data || (node.data = {})
                        const hProps = data.hProperties || (data.hProperties = {})
                        node.data.hProperties = Object.assign({}, hProps, prop)
                        node.children[0].value = text
                    }
                }
            }
        })
        return tree
    }
    return transformer
}

module.exports = remarkCustomAttrs

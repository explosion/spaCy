import { visit } from 'unist-util-visit'
import { replacements } from '../meta/dynamicMeta.mjs'

const prefix = '%%'

// Attaches prefix to the start of the string.
const attachPrefix = (str) => (prefix || '') + str

// RegExp to find any replacement keys.
const regexp = RegExp(
    '(' +
        Object.keys(replacements)
            .map((key) => attachPrefix(key))
            .join('|') +
        ')',
    'g'
)

// Removes prefix from the start of the string.
const stripPrefix = (str) => (prefix ? str.replace(RegExp(`^${prefix}`), '') : str)

const replacer = (_match, name) => replacements[stripPrefix(name)]

const remarkFindAndReplace = () => (markdownAST) => {
    // Go through all text, html, code, inline code, and links.
    visit(markdownAST, ['text', 'html', 'code', 'link'], (node) => {
        if (node.type === 'link') {
            // For links, the text value is replaced by text node, so we change the
            // URL value.
            const processedText = node.url.replace(regexp, replacer)
            node.url = processedText
        } else {
            // For all other nodes, replace the node value.
            const processedText = node.value.replace(regexp, replacer)
            node.value = processedText
        }
    })

    return markdownAST
}

export default remarkFindAndReplace

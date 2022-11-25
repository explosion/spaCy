/**
 * Support titles, line highlights and more for code blocks
 */
import { Parser } from 'acorn'
import { visit } from 'unist-util-visit'
import parseAttr from 'md-attr-parser'

import getProps from './getProps.mjs'

const defaultOptions = {
    defaultPrefix: '###',
    prefixMap: {
        javascript: '///',
        jsx: '///',
    },
    languageAliases: {},
    prompts: ['$'],
}

function remarkCodeBlocks(userOptions = {}) {
    const options = Object.assign({}, defaultOptions, userOptions)

    function transformer(tree) {
        visit(tree, 'code', (node) => {
            if (node.value) {
                const langName = node.lang || 'none'
                const lang = options.languageAliases[langName] || langName
                const prefix = options.prefixMap[lang] || options.defaultPrefix
                const lines = node.value.split('\n')
                let attrs = { lang }
                const firstLine = lines[0].trim()
                if (firstLine && firstLine.startsWith(prefix)) {
                    const title = firstLine.slice(prefix.length).trim()
                    attrs.title = title
                    // Check for attributes in title, e.g. {executable="true"}
                    const parsed = title.split(/\{(.*?)\}/)
                    if (parsed.length >= 2 && parsed[1]) {
                        const { prop } = parseAttr(parsed[1])
                        attrs = { ...attrs, ...prop, title: parsed[0].trim(), lang }
                    }
                    // Overwrite the code text with the rest of the lines
                    node.value = lines.slice(1).join('\n')
                } else if (
                    (firstLine && /^https:\/\/github.com/.test(firstLine)) ||
                    firstLine.startsWith('%%GITHUB_')
                ) {
                    // GitHub URL
                    attrs.github = node.value
                }

                const data = node.data || (node.data = {})
                const hProps = data.hProperties || (data.hProperties = {})

                const meta = getProps(Parser.parse(node.meta, { ecmaVersion: 'latest' }))

                node.data.hProperties = Object.assign({}, hProps, attrs, meta)
            }
        })

        visit(tree, 'inlineCode', (node) => {
            node.type = 'mdxJsxTextElement'
            node.name = 'InlineCode'
            node.children = [
                {
                    type: 'text',
                    value: node.value,
                },
            ]
            node.data = { _mdxExplicitJsx: true }
        })

        return tree
    }
    return transformer
}

export default remarkCodeBlocks

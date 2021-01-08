/**
 * Support titles, line highlights and more for code blocks
 */

const visit = require('unist-util-visit')
const parseAttr = require('md-attr-parser')

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
        visit(tree, 'code', node => {
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
                    attrs.github = 'true'
                }
                // If it's a bash code block and single line, check for prompts
                if (lang === 'bash') {
                    const [trueFirstLine, ...trueLines] = node.value.split('\n')
                    for (let prompt of options.prompts) {
                        if (trueFirstLine.startsWith(prompt)) {
                            const content = [
                                trueFirstLine.slice(prompt.length).trim(),
                                ...trueLines,
                            ]
                            attrs.prompt = prompt
                            node.value = content.join('\n')
                            break
                        }
                    }
                }

                const data = node.data || (node.data = {})
                const hProps = data.hProperties || (data.hProperties = {})
                node.data.hProperties = Object.assign({}, hProps, attrs)
            }
        })
        return tree
    }
    return transformer
}

module.exports = remarkCodeBlocks

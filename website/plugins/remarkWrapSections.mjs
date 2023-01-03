/**
 * Check the tree for headlines of a certain depth and wrap the headline and
 * all content up to the next headline in a section.
 * Based on: https://github.com/luhmann/tufte-markdown
 */

import { visit } from 'unist-util-visit'

const defaultOptions = {
    element: 'section',
    prefix: 'section-',
    depth: 2,
    slugify: true,
}

function remarkWrapSection(userOptions = {}) {
    const options = Object.assign({}, defaultOptions, userOptions)

    function transformer(tree) {
        const headingsMap = []
        const newTree = []

        visit(tree, 'import', (node) => {
            // For compatibility with MDX / gatsby-mdx, make sure import nodes
            // are not moved further down into children (which means they're not
            // recognized and interpreted anymore). Add them to the very start
            // of the tree.
            newTree.push(node)
        })

        visit(tree, 'heading', (node, index) => {
            if (node.depth === options.depth) {
                const data = node.data || (node.data = {})
                const hProps = data.hProperties || (data.hProperties = {})
                headingsMap.push({ index, id: hProps.id })
            }
        })

        if (headingsMap.length) {
            for (let index = 0; index <= headingsMap.length; index++) {
                const sectionStartIndex = index === 0 ? 0 : headingsMap[index - 1].index
                const sectionEndIndex =
                    index === headingsMap.length ? tree.children.length : headingsMap[index].index
                const children = tree.children
                    .slice(sectionStartIndex, sectionEndIndex)
                    .filter((node) => node.type !== 'import')

                if (children.length) {
                    const headingId = index === 0 ? 0 : headingsMap[index - 1].id
                    const sectionId = headingId ? options.prefix + headingId : undefined
                    const wrapperNode = {
                        type: 'section',
                        children,
                        data: { hName: options.element, hProperties: { id: sectionId } },
                    }
                    newTree.push(wrapperNode)
                }
            }
            tree.children = newTree
        }
        return tree
    }
    return transformer
}

export default remarkWrapSection

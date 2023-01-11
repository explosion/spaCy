import getProps from './getProps.mjs'

const handleNode = (node) => {
    if (node.type === 'section' && node.children) {
        return {
            ...node,
            children: node.children.map(handleNode),
        }
    }

    if (node.type !== 'heading' || !node.children || node.children < 2) {
        return node
    }

    const indexLast = node.children.length - 1
    const lastNode = node.children[indexLast]

    if (lastNode.type !== 'mdxTextExpression' || !lastNode.data || !lastNode.data.estree) {
        return node
    }

    const data = node.data || (node.data = {})
    data.hProperties = getProps(lastNode.data.estree)

    // Only keep the text, drop the rest
    node.children = [node.children[0]]

    return node
}

const parseAstTree = (markdownAST) => ({
    ...markdownAST,
    children: markdownAST.children.map(handleNode),
})

const remarkCustomAttrs = () => parseAstTree

export default remarkCustomAttrs

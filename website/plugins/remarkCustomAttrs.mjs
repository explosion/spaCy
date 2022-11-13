const parseAttribute = (expression) => {
    if (expression.type !== 'AssignmentExpression' || !expression.left || !expression.right) {
        return
    }

    const { left, right } = expression

    if (left.type !== 'Identifier' || right.type !== 'Literal' || !left.name || !right.value) {
        return
    }

    return { type: 'mdxJsxAttribute', name: left.name, value: right.value }
}

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

    const { estree } = lastNode.data

    if (estree.type !== 'Program' || !estree.body || estree.body.length <= 0 || !estree.body[0]) {
        return node
    }

    const estreeBodyFirstNode = estree.body[0]

    if (estreeBodyFirstNode.type !== 'ExpressionStatement' || !estreeBodyFirstNode.expression) {
        return node
    }

    const statement = estreeBodyFirstNode.expression

    const attributeExpressions = [
        ...(statement.type === 'SequenceExpression' && statement.expressions
            ? statement.expressions
            : []),
        ...(statement.type === 'AssignmentExpression' ? [statement] : []),
    ]

    // This replaces the markdown heading with a JSX element
    return {
        type: 'mdxJsxFlowElement',
        name: `h${node.depth}`,
        attributes: attributeExpressions.map(parseAttribute),
        children: [node.children[0]],
    }
}

const parseAstTree = (markdownAST) => ({
    ...markdownAST,
    children: markdownAST.children.map(handleNode),
})

const remarkCustomAttrs = () => parseAstTree

export default remarkCustomAttrs

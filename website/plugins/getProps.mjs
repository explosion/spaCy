const parseAttribute = (expression) => {
    if (expression.type !== 'AssignmentExpression' || !expression.left || !expression.right) {
        return
    }

    const { left, right } = expression

    if (left.type !== 'Identifier' || right.type !== 'Literal' || !left.name || !right.value) {
        return
    }

    return [left.name, right.value]
}

const getProps = (estree) => {
    if (estree.type !== 'Program' || !estree.body || estree.body.length <= 0 || !estree.body[0]) {
        return {}
    }

    const estreeBodyFirstNode =
        estree.body[0].type === 'BlockStatement' ? estree.body[0].body[0] : estree.body[0]

    if (estreeBodyFirstNode.type !== 'ExpressionStatement' || !estreeBodyFirstNode.expression) {
        return {}
    }

    const statement = estreeBodyFirstNode.expression

    const attributeExpressions = [
        ...(statement.type === 'SequenceExpression' && statement.expressions
            ? statement.expressions
            : []),
        ...(statement.type === 'AssignmentExpression' ? [statement] : []),
    ]

    return Object.fromEntries(attributeExpressions.map(parseAttribute))
}

export default getProps

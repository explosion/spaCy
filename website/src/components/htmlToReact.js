import { Parser as HtmlToReactParser } from 'html-to-react'

const htmlToReactParser = new HtmlToReactParser()
/**
 * Convert raw HTML to React elements
 * @param {string} html - The HTML markup to convert.
 * @returns {Node} - The converted React elements.
 */

export default function htmlToReact(html) {
    return htmlToReactParser.parse(html)
}

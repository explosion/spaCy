import React, { useEffect, useState } from 'react'
import { serialize } from 'next-mdx-remote/serialize'
import { MDXRemote } from 'next-mdx-remote'
import remarkPlugins from '../../plugins/index.mjs'

/**
 * Convert raw Markdown to React
 * @param {String} markdown - The Markdown markup to convert.
 * @param {Object} [remarkReactComponents] - Optional React components to use
 *  for HTML elements.
 * @returns {Node} - The converted React elements.
 */
export default function MarkdownToReact({ markdown }) {
    const [mdx, setMdx] = useState(null)

    useEffect(() => {
        const getMdx = async () => {
            setMdx(
                await serialize(markdown, {
                    parseFrontmatter: false,
                    mdxOptions: {
                        remarkPlugins,
                    },
                })
            )
        }

        getMdx()
    }, [markdown])

    return mdx ? <MDXRemote {...mdx} /> : <></>
}

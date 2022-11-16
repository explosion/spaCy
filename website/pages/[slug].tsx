import type { GetStaticPaths, GetStaticProps } from 'next'
import { serialize } from 'next-mdx-remote/serialize'
import fs from 'fs'
import { MDXRemote, MDXRemoteSerializeResult } from 'next-mdx-remote'
import path from 'path'
import Layout from '../components/layout'
import remarkPlugins from '../plugins/index.mjs'

type PropsPage = {
    mdx: MDXRemoteSerializeResult
}

const PostPage = ({ mdx: mdx }: PropsPage) => {
    return (
        <Layout>
            <MDXRemote {...mdx} />
        </Layout>
    )
}

export default PostPage

type ParsedUrlQuery = {
    slug: string
}

export const getStaticPaths: GetStaticPaths<ParsedUrlQuery> = async () => {
    // This function needs to be defined inside `getStaticPath` to be executed in executed in the correct context
    const loadFolder = (): Array<{ params: ParsedUrlQuery }> =>
        fs
            .readdirSync(path.join('docs'))
            .map((filename) => ({
                params: {
                    slug: filename.replace('.mdx', ''),
                },
            }))

    return {
        paths: loadFolder(),
        fallback: false,
    }
}

export const getStaticProps: GetStaticProps<PropsPage, ParsedUrlQuery> = async (args) => {
    if (!args.params) {
        return { notFound: true }
    }
    return {
        props: {
            slug: args.params.slug,
            mdx: await serialize(
                fs.readFileSync(path.join('docs', args.params.slug + '.mdx'), 'utf-8'),
                {
                    parseFrontmatter: true,
                    mdxOptions: {
                        remarkPlugins,
                    },
                }
            ),
        },
    }
}

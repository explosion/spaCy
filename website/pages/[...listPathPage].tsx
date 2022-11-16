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
    listPathPage: Array<string>
}

export const getStaticPaths: GetStaticPaths<ParsedUrlQuery> = async () => {
    // This function needs to be defined inside `getStaticPath` to be executed in executed in the correct context
    const loadFolder = (pathBase: Array<string> = []): Array<{ params: ParsedUrlQuery }> =>
        fs
            .readdirSync(path.join('docs', ...pathBase), { withFileTypes: true })
            .flatMap((dirent: fs.Dirent) => {
                if (dirent.isDirectory()) {
                    return loadFolder([...pathBase, dirent.name])
                }
                if (!dirent.name.includes('.mdx')) {
                    return []
                }

                return {
                    params: {
                        listPathPage: [...pathBase, dirent.name.replace('.mdx', '')],
                    },
                }
            })

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
            mdx: await serialize(
                fs.readFileSync(`${path.join('docs', ...args.params.listPathPage)}.mdx`, 'utf-8'),
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

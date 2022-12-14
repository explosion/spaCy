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
                        listPathPage:
                            dirent.name === 'index.mdx'
                                ? pathBase
                                : [...pathBase, dirent.name.replace('.mdx', '')],
                    },
                }
            })

    return {
        paths: loadFolder(),
        fallback: false,
    }
}

const getPathFileWithExtension = (listPathFile: ReadonlyArray<string>) =>
    `${path.join(...listPathFile)}.mdx`

export const getStaticProps: GetStaticProps<PropsPage, ParsedUrlQuery> = async (args) => {
    if (!args.params) {
        return { notFound: true }
    }

    const listPathFile = ['docs', ...args.params.listPathPage]
    const isIndex = fs.existsSync(getPathFileWithExtension(listPathFile)) !== true
    const listPathFileWithIndex = isIndex ? [...listPathFile, 'index'] : listPathFile
    const listPathFileWithIndexAndExtension = getPathFileWithExtension(listPathFileWithIndex)

    const mdx = await serialize(fs.readFileSync(listPathFileWithIndexAndExtension, 'utf-8'), {
        parseFrontmatter: true,
        mdxOptions: {
            remarkPlugins,
        },
    })

    return {
        props: {
            mdx,
        },
    }
}

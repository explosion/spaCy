import type { GetStaticPaths, GetStaticProps } from 'next'
import { serialize } from 'next-mdx-remote/serialize'
import fs from 'fs'
import { MDXRemote, MDXRemoteSerializeResult } from 'next-mdx-remote'
import path from 'path'
import Layout from '../src/templates'
import remarkPlugins from '../plugins/index.mjs'

import recordSection from '../meta/recordSections'

type ApiDetails = {
    stringName: string | null
    baseClass: {
        title: string
        slug: string
    } | null
    trainable: string | null
}

type PropsPage = {
    mdx: MDXRemoteSerializeResult

    /**
     * TODO: This is only here for legacy support of the old code base
     * It should be refactort to pass the file path and page path instead.
     */
    slug: string
    sectionTitle: string | null
    theme: string | null
    section: string
    apiDetails: ApiDetails
    isIndex: boolean
}

const PostPage = ({ mdx: mdx, ...props }: PropsPage) => {
    return (
        <Layout {...props}>
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
    const pathFileWithIndexAndExtension = getPathFileWithExtension(listPathFileWithIndex)

    const mdx = await serialize(fs.readFileSync(pathFileWithIndexAndExtension, 'utf-8'), {
        parseFrontmatter: true,
        mdxOptions: {
            remarkPlugins,
        },
    })

    if (!mdx.frontmatter) {
        throw new Error(`Frontmatter missing for ${pathFileWithIndexAndExtension}`)
    }

    const parentFolder =
        listPathFileWithIndex.length > 1
            ? listPathFileWithIndex[listPathFileWithIndex.length - 2]
            : null
    const section = mdx.frontmatter.section ?? parentFolder
    const sectionMeta = section ? recordSection[section] ?? null : null
    const baseClass = null
    const apiDetails: ApiDetails = {
        stringName: mdx.frontmatter.api_string_name ?? null,
        baseClass: baseClass
            ? {
                  title: mdx.frontmatter.title,
                  slug: mdx.frontmatter.api_base_class,
              }
            : null,
        trainable: mdx.frontmatter.api_trainable ?? null,
    }

    return {
        props: {
            ...mdx.frontmatter,
            slug: `/${args.params.listPathPage.join('/')}`,
            mdx,
            sectionTitle: sectionMeta?.title ?? null,
            theme: sectionMeta?.theme ?? null,
            section: section,
            apiDetails: apiDetails,
            isIndex,
        },
    }
}

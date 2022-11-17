import type { GetStaticPaths, GetStaticProps } from 'next'
import models from '../../meta/languages.json'
import recordSection from '../../meta/recordSections'
import recordLanguages from '../../meta/recordLanguages'
import Layout from '../../src/components/layout'

type PropsPageModel = {
    id: string
    slug: ReadonlyArray<string>
    isIndex: false
    title: string
    section: 'models'
    sectionTitle: string
    theme: string
    next: { title: string; slug: string } | null
    meta: { models?: ReadonlyArray<string>; example?: string; hasExamples?: boolean }
}

const PostPageModel = (props: PropsPageModel) => {
    return <Layout {...props} />
}

export default PostPageModel

export const getStaticPaths: GetStaticPaths<{ slug: string }> = async () => {
    return {
        paths: models.languages
            .filter(({ models }) => models && models.length)
            .map((language) => `/models/${language.code}`),
        fallback: false,
    }
}

export const getStaticProps: GetStaticProps<
    PropsPageModel,
    {
        slug: string
    }
> = async (args) => {
    if (args.params === undefined) {
        return { notFound: true }
    }

    const language = recordLanguages[args.params.slug]

    return {
        props: {
            id: language.code,
            slug: ['models', language.code],
            isIndex: false,
            title: language.name,
            section: 'models',
            sectionTitle: recordSection.models.title,
            theme: recordSection.models.theme,
            next: language.next
                ? { title: language.next.name, slug: `/models/${language.next.code}` }
                : null,
            meta: {
                models: language.models || null,
                example: language.example || null,
                hasExamples: language.has_examples || null,
            },
        },
    }
}

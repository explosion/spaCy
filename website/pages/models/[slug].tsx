import type { GetStaticPaths, GetStaticProps } from 'next'
import models from '../../meta/languages.json'
import recordSection from '../../meta/recordSections'
import recordLanguages from '../../meta/recordLanguages'
import Layout from '../../src/templates'
import { PropsPageBase } from '../[...listPathPage]'
import { languagesSorted } from '../../meta/languageSorted'

type PropsPageModel = PropsPageBase & {
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
    const getSlug = (languageCode: string) => `/${['models', languageCode].join('/')}`

    if (args.params === undefined) {
        return { notFound: true }
    }

    const language = recordLanguages[args.params.slug]

    const nextLanguage = languagesSorted.find(
        (item, index) => index > 0 && languagesSorted[index - 1].code === language.code
    )

    return {
        props: {
            id: language.code,
            slug: getSlug(language.code),
            isIndex: false,
            title: language.name,
            section: 'models',
            sectionTitle: recordSection.models.title,
            theme: recordSection.models.theme,
            next: nextLanguage
                ? { title: nextLanguage.name, slug: getSlug(nextLanguage.code) }
                : null,
            meta: {
                models: language.models || null,
                example: language.example || null,
                hasExamples: language.has_examples || null,
            },
        },
    }
}

import { GetStaticPaths, GetStaticProps } from 'next'
import recordSections from '../../../meta/recordSections'
import { recordUniverseCategories } from '../../../meta/recordUniverse'
import universe from '../../../meta/universe.json'
import Layout from '../../../src/templates'
import { PropsPageBase } from '../../[...listPathPage]'

type ParsedUrlQuery = {
    slug: string
}

export default Layout

export const getStaticPaths: GetStaticPaths<ParsedUrlQuery> = async () => {
    return {
        paths: universe.categories.flatMap((category) =>
            category.items.map((item) => `/universe/category/${item.id}`)
        ),
        fallback: false,
    }
}

export const getStaticProps: GetStaticProps<PropsPageBase, ParsedUrlQuery> = async (args) => {
    if (!args.params) {
        return { notFound: true }
    }

    const item = recordUniverseCategories[args.params.slug]

    return {
        props: {
            id: item.id,
            title: item.title,
            teaser: item.description,
            slug: `/universe/category/${args.params.slug}`,
            isIndex: false,
            data: { ...item, isCategory: true },
            section: 'universe',
            sectionTitle: recordSections.universe.title,
            theme: recordSections.universe.theme,
        },
    }
}

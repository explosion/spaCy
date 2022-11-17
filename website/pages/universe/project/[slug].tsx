import { GetStaticPaths, GetStaticProps } from 'next'
import recordSections from '../../../meta/recordSections'
import { recordUniverseResources } from '../../../meta/recordUniverse'
import universe from '../../../meta/universe.json'
import Layout from '../../../src/components/layout'

type ParsedUrlQuery = {
    slug: string
}

type PropsPage = {
    slug: ReadonlyArray<string>
    sectionTitle: string | null
    theme: string | null
    section: string
    isIndex: boolean
}

export default Layout

export const getStaticPaths: GetStaticPaths<ParsedUrlQuery> = async () => {
    return {
        paths: universe.resources.flatMap((resource) => `/universe/project/${resource.id}`),
        fallback: false,
    }
}

export const getStaticProps: GetStaticProps<PropsPage, ParsedUrlQuery> = async (args) => {
    if (!args.params) {
        return { notFound: true }
    }

    const resource = recordUniverseResources[args.params.slug]

    return {
        props: {
            id: resource.id,
            title: resource.title || resource.id,
            teaser: resource.slogan || null,
            slug: args.params.slug.split('/'),
            isIndex: false,
            data: { ...resource, isProject: true },
            section: 'universe',
            sectionTitle: recordSections.universe.title,
            theme: recordSections.universe.theme,
        },
    }
}

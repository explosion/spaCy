import { GetStaticPaths, GetStaticProps } from 'next'
import recordSections from '../../../meta/recordSections'
import { recordUniverseResources } from '../../../meta/recordUniverse'
import universe from '../../../meta/universe.json'
import Layout from '../../../src/templates'
import { PropsPageBase } from '../../[...listPathPage]'

type ParsedUrlQuery = {
    slug: string
}

export default Layout

export const getStaticPaths: GetStaticPaths<ParsedUrlQuery> = async () => {
    return {
        paths: universe.resources.flatMap((resource) => `/universe/project/${resource.id}`),
        fallback: false,
    }
}

export const getStaticProps: GetStaticProps<PropsPageBase, ParsedUrlQuery> = async (args) => {
    if (!args.params) {
        return { notFound: true }
    }

    const resource = recordUniverseResources[args.params.slug]

    return {
        props: {
            id: resource.id,
            title: resource.title || resource.id,
            teaser: resource.slogan || null,
            slug: `/universe/project/${args.params.slug}`,
            isIndex: false,
            data: { ...resource, isProject: true },
            section: 'universe',
            sectionTitle: recordSections.universe.title,
            theme: recordSections.universe.theme,
        },
    }
}

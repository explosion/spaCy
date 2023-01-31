import recordSections from '../../meta/recordSections'
import Layout from '../../src/templates'

const Universe = () => {
    return (
        <Layout
            slug={'/universe'}
            section="universe"
            sectionTitle={recordSections.universe.title}
            theme={recordSections.universe.theme}
            isIndex
            title="Overview"
        />
    )
}

export default Universe

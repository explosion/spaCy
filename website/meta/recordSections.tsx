import siteMetadata from './site.json'

const recordSections = Object.fromEntries(siteMetadata.sections.map((s) => [s.id, s]))

export default recordSections

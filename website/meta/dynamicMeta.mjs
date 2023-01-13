import site from './site.json' assert { type: 'json' }

export const domain = process.env.BRANCH || site.domain
export const siteUrl = `https://${domain}`
export const nightly = site.nightlyBranches.includes(domain)
export const legacy = site.legacy || !!+process.env.SPACY_LEGACY
export const binderBranch = domain
export const branch = nightly ? 'develop' : 'master'
export const replacements = {
    GITHUB_SPACY: `https://github.com/explosion/spaCy/tree/${branch}`,
    GITHUB_PROJECTS: `https://github.com/${site.projectsRepo}`,
    SPACY_PKG_NAME: nightly ? 'spacy-nightly' : 'spacy',
    SPACY_PKG_FLAGS: nightly ? ' --pre' : '',
}

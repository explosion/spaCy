const site = require('./site.json')

const domain = process.env.BRANCH || site.domain

module.exports = {
    domain,
    siteUrl: `https://${domain}`,
    nightly: site.nightlyBranches.includes(domain),
    legacy: site.legacy || !!+process.env.SPACY_LEGACY,
    binderBranch: domain,
}

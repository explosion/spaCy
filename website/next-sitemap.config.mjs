import { siteUrl } from './meta/dynamicMeta.mjs'

/** @type {import('next-sitemap').IConfig} */
const config = {
    siteUrl,
    generateRobotsTxt: true,
    autoLastmod: false,
}

export default config

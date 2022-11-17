import MDX from '@next/mdx'

import remarkPlugins from './plugins/index.mjs'

const withMDX = MDX({
    extension: /\.mdx?$/,
    options: {
        remarkPlugins,
        providerImportSource: '@mdx-js/react',
    },
    experimental: {
        mdxRs: true,
    },
})

/** @type {import('next').NextConfig} */
const nextConfig = withMDX({
    reactStrictMode: true,
    swcMinify: true,
    pageExtensions: ['js', 'jsx', 'ts', 'tsx', 'md', 'mdx'],
    eslint: {
        ignoreDuringBuilds: true,
    },
})

export default nextConfig

import MDX from '@next/mdx'

const withMDX = MDX({
    extension: /\.mdx?$/,
    options: {
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
})

export default nextConfig

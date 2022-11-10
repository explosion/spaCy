const withMDX = require('@next/mdx')({
    extension: /\.mdx?$/,
    options: {
        providerImportSource: '@mdx-js/react',
    },
})

/** @type {import('next').NextConfig} */
const nextConfig = withMDX({
    reactStrictMode: true,
    swcMinify: true,
    pageExtensions: ['js', 'jsx', 'ts', 'tsx', 'md', 'mdx'],
})

module.exports = nextConfig

import MDX from '@next/mdx'
import PWA from 'next-pwa'
import defaultRuntimeCaching from 'next-pwa/cache.js'

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

const withPWA = PWA({
    dest: 'public',
    disable: process.env.NODE_ENV === 'development',
    // The default rules match images by file extension, which never matches an
    // Image CDN URL like `/.netlify/images?url=…&w=650`. Without this entry those
    // renditions bypass the service worker cache and are refetched on every visit.
    runtimeCaching: [
        {
            urlPattern: /\/\.netlify\/images\?.+$/i,
            handler: 'StaleWhileRevalidate',
            options: {
                cacheName: 'netlify-image-cdn',
                expiration: {
                    maxEntries: 64,
                    maxAgeSeconds: 30 * 24 * 60 * 60, // 30 days
                },
            },
        },
        ...defaultRuntimeCaching,
    ],
})

/** @type {import('next').NextConfig} */
const nextConfig = withPWA(
    withMDX({
        reactStrictMode: true,
        swcMinify: true,
        pageExtensions: ['js', 'jsx', 'ts', 'tsx', 'md', 'mdx'],
        eslint: {
            ignoreDuringBuilds: true,
        },
        typescript: {
            ignoreBuildErrors: true,
        },
        images: { unoptimized: true },
        env: {
            DOCSEARCH_API_KEY: process.env.DOCSEARCH_API_KEY,
        },
    })
)

export default nextConfig

import '../src/styles/layout.sass'
import '../src/styles/search.sass'

import type { AppProps } from 'next/app'
import Head from 'next/head'
import PlausibleProvider from 'next-plausible'
import { MDXProvider } from '@mdx-js/react'
import { remarkComponents } from '../src/remark'
import { domain } from '../meta/dynamicMeta.mjs'

export default function App({ Component, pageProps }: AppProps) {
    return (
        <PlausibleProvider domain={domain} enabled>
            <Head>
                <link rel="sitemap" type="application/xml" href="/sitemap.xml" />
                <link rel="shortcut icon" href="/icons/icon-192x192.png" />
                <link rel="manifest" href="/manifest.webmanifest" />
                <meta
                    name="viewport"
                    content="width=device-width, initial-scale=1.0, minimum-scale=1, maximum-scale=5.0, shrink-to-fit=no, viewport-fit=cover"
                />
                <meta name="theme-color" content="#09a3d5" />
                <link rel="apple-touch-icon" sizes="192x192" href="/icons/icon-192x192.png" />
                <link rel="apple-touch-icon" sizes="256x256" href="/icons/icon-256x256.png" />
                <link rel="apple-touch-icon" sizes="384x384" href="/icons/icon-384x384.png" />
                <link rel="apple-touch-icon" sizes="512x512" href="/icons/icon-512x512.png" />
            </Head>
            <MDXProvider components={remarkComponents}>
                <Component {...pageProps} />
            </MDXProvider>
        </PlausibleProvider>
    )
}

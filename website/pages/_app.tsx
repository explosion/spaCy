import '../src/styles/layout.sass'
import type { AppProps } from 'next/app'
import Head from 'next/head'
import { MDXProvider } from '@mdx-js/react'
import { remarkComponents } from '../src/remark'

export default function App({ Component, pageProps }: AppProps) {
    return (
        <>
            <Head>
                <link rel="sitemap" type="application/xml" href="/sitemap.xml" />
            </Head>
            <MDXProvider components={remarkComponents}>
                <Component {...pageProps} />
            </MDXProvider>
        </>
    )
}

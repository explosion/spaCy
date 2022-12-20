import type { AppProps } from 'next/app'
import { MDXProvider } from '@mdx-js/react'
import mdxComponents from '../components/mdxComponents'

export default function App({ Component, pageProps }: AppProps) {
    return (
        <MDXProvider components={mdxComponents}>
            <Component {...pageProps} />
        </MDXProvider>
    )
}

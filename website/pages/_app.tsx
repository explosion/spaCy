import type { AppProps } from 'next/app'
import { MDXProvider } from '@mdx-js/react'
import { remarkComponents } from '../src/remark'

export default function App({ Component, pageProps }: AppProps) {
    return (
        <MDXProvider components={remarkComponents}>
            <Component {...pageProps} />
        </MDXProvider>
    )
}

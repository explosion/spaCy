import { navigate } from 'gatsby'

import './src/styles/layout.sass'
import Juniper from './src/components/juniper'
import 'intersection-observer'

// Workaround to rewrite anchor links
const clientSideRewrites = {
    '/usage/linguistic-features/#rule-based-matching': '/usage/rule-based-matching',
}

/* eslint-disable */
import HKGroteskSemiBoldWOFF from './src/fonts/hkgrotesk-semibold.woff'
import HKGroteskSemiBoldWOFF2 from './src/fonts/hkgrotesk-semibold.woff2'
import HKGroteskSemiBoldItalicWOFF from './src/fonts/hkgrotesk-semibolditalic.woff'
import HKGroteskSemiBoldItalicWOFF2 from './src/fonts/hkgrotesk-semibolditalic.woff2'
import HKGroteskBoldWOFF from './src/fonts/hkgrotesk-bold.woff'
import HKGroteskBoldWOFF2 from './src/fonts/hkgrotesk-bold.woff2'
import HKGroteskBoldItalicWOFF from './src/fonts/hkgrotesk-bolditalic.woff'
import HKGroteskBoldItalicWOFF2 from './src/fonts/hkgrotesk-bolditalic.woff2'
/* eslint-enable */

export const onInitialClientRender = () => {
    // Importing Juniper in the component currently causes various problems
    // because of the global window reference in its dependencies. So this
    // is kinda hacky at the moment.
    window.Juniper = Juniper
}

export const onRouteUpdate = ({ location }) => {
    window.dispatchEvent(new Event('resize')) // for progress
    window.dispatchEvent(new Event('scroll')) // for progress
    if (location.hash) {
        // Client-side rewrites
        const rewrite = clientSideRewrites[location.pathname + location.hash]
        if (rewrite) {
            navigate(rewrite)
            return
        }
        setTimeout(() => {
            const el = document.querySelector(`${location.hash}`)
            if (el) {
                // Navigate to targeted element
                el.scrollIntoView()
                // Force recomputing :target pseudo class with pushState/popState
                window.location.hash = location.hash
            }
        }, 0)
    }
}

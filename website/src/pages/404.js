import React from 'react'
import { window } from 'browser-monads'

import Layout from '../components/layout/index'
import { LandingHeader, LandingTitle } from '../components/landing'
import Button from '../components/button'
import { nightly, legacy } from '../../meta/dynamicMeta'

const page404 = ({ location }) => {
    const pageContext = { title: '404 Error', searchExclude: true, isIndex: false }
    return (
        <Template pageContext={pageContext} location={location}>
            <LandingHeader style={{ minHeight: 400 }} nightly={nightly} legacy={legacy}>
                <LandingTitle>
                    Ooops, this page
                    <br />
                    does not exist!
                </LandingTitle>
                <br />
                <Button onClick={() => window.history.go(-1)} variant="tertiary">
                    Click here to go back
                </Button>
            </LandingHeader>
        </Template>
    )
}

export default page404

import React from 'react'
import { window } from 'browser-monads'

import { LandingHeader, LandingTitle } from '../components/landing'
import Button from '../components/button'

export default () => (
    <LandingHeader style={{ minHeight: 400 }}>
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
)

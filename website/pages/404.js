import React from 'react'
import { window } from 'browser-monads'
import classNames from 'classnames'

import Template from '../src/templates/index'
import { LandingHeader, LandingTitle } from '../src/components/landing'
import { nightly, legacy } from '../meta/dynamicMeta'
import classes from '../src/styles/button.module.sass'

const page404 = () => {
    const pageContext = { title: '404 Error', searchExclude: true, isIndex: false }
    return (
        <Template {...pageContext}>
            <LandingHeader style={{ minHeight: 400 }} nightly={nightly} legacy={legacy}>
                <LandingTitle>
                    Ooops, this page
                    <br />
                    does not exist!
                </LandingTitle>
                <br />
                <button
                    onClick={() => window.history.go(-1)}
                    className={classNames(classes.root, classes.tertiary)}
                >
                    Click here to go back
                </button>
            </LandingHeader>
        </Template>
    )
}

export default page404

import React from 'react'
import { window } from 'browser-monads'
import { graphql } from 'gatsby'

import Template from '../templates/index'
import { LandingHeader, LandingTitle } from '../components/landing'
import Button from '../components/button'

export default ({ data, location }) => {
    const { nightly, legacy } = data.site.siteMetadata
    const pageContext = { title: '404 Error', searchExclude: true, isIndex: false }
    return (
        <Template data={data} pageContext={pageContext} location={location}>
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

export const pageQuery = graphql`
    query {
        site {
            siteMetadata {
                nightly
                legacy
                title
                description
                navigation {
                    text
                    url
                }
                docSearch {
                    apiKey
                    indexName
                }
            }
        }
    }
`

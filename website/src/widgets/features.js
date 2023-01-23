import React from 'react'
import { graphql, StaticQuery } from 'gatsby'

import { Ul, Li } from '../components/list'

export default () => (
    <StaticQuery
        query={query}
        render={({ site }) => {
            const { counts } = site.siteMetadata
            return (
                <Ul>
                    <Li>
                        ✅ Support for <strong>{counts.langs}+ languages</strong>
                    </Li>
                    <Li>
                        ✅ <strong>{counts.models} trained pipelines</strong> for{' '}
                        {counts.modelLangs} languages
                    </Li>
                    <Li>
                        ✅ Multi-task learning with pretrained <strong>transformers</strong> like
                        BERT
                    </Li>
                    <Li>
                        ✅ Pretrained <strong>word vectors</strong>
                    </Li>
                    <Li>✅ State-of-the-art speed</Li>
                    <Li>
                        ✅ Production-ready <strong>training system</strong>
                    </Li>
                    <Li>
                        ✅ Linguistically-motivated <strong>tokenization</strong>
                    </Li>
                    <Li>
                        ✅ Components for <strong>named entity</strong> recognition, part-of-speech
                        tagging, dependency parsing, sentence segmentation,{' '}
                        <strong>text classification</strong>, lemmatization, morphological analysis,
                        entity linking and more
                    </Li>
                    <Li>
                        ✅ Easily extensible with <strong>custom components</strong> and attributes
                    </Li>
                    <Li>
                        ✅ Support for custom models in <strong>PyTorch</strong>,{' '}
                        <strong>TensorFlow</strong> and other frameworks
                    </Li>
                    <Li>
                        ✅ Built in <strong>visualizers</strong> for syntax and NER
                    </Li>
                    <Li>
                        ✅ Easy <strong>model packaging</strong>, deployment and workflow management
                    </Li>
                    <Li>✅ Robust, rigorously evaluated accuracy</Li>
                </Ul>
            )
        }}
    />
)

const query = graphql`
    query FeaturesQuery {
        site {
            siteMetadata {
                counts {
                    langs
                    modelLangs
                    models
                }
            }
        }
    }
`

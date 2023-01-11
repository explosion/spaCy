import React from 'react'

import { Ul, Li } from '../components/list'

import models from '../../meta/languages.json'

/**
 * Compute the overall total counts of models and languages
 */
function getCounts(langs = []) {
    return {
        langs: langs.length,
        modelLangs: langs.filter(({ models }) => models && !!models.length).length,
        models: langs.map(({ models }) => (models ? models.length : 0)).reduce((a, b) => a + b, 0),
    }
}

const Features = () => {
    const counts = getCounts(models.languages)
    return (
        <Ul>
            <Li>
                ✅ Support for <strong>{counts.langs}+ languages</strong>
            </Li>
            <Li>
                ✅ <strong>{counts.models} trained pipelines</strong> for {counts.modelLangs}{' '}
                languages
            </Li>
            <Li>
                ✅ Multi-task learning with pretrained <strong>transformers</strong> like BERT
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
                ✅ Components for <strong>named entity</strong> recognition, part-of-speech tagging,
                dependency parsing, sentence segmentation, <strong>text classification</strong>,
                lemmatization, morphological analysis, entity linking and more
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
}

export default Features
